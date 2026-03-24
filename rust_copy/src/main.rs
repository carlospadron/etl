use bytes::{Bytes, BytesMut};
use std::env;
use tokio_postgres::{Client, NoTls};

async fn connect(
    host: &str,
    port: &str,
    user: &str,
    password: &str,
    dbname: &str,
) -> Client {
    let conn_str = format!(
        "host={host} port={port} user={user} password={password} dbname={dbname}"
    );
    let (client, conn) = tokio_postgres::connect(&conn_str, NoTls)
        .await
        .expect("connection failed");
    tokio::spawn(async move {
        if let Err(e) = conn.await {
            eprintln!("connection error: {e}");
        }
    });
    client
}

#[tokio::main]
async fn main() {
    let src_host = env::var("ORIGIN_ADDRESS").expect("ORIGIN_ADDRESS");
    let src_port = env::var("ORIGIN_PORT").unwrap_or_else(|_| "5432".into());
    let src_user = env::var("ORIGIN_USER").expect("ORIGIN_USER");
    let src_pass = env::var("ORIGIN_PASS").expect("ORIGIN_PASS");
    let src_db = env::var("ORIGIN_DB").expect("ORIGIN_DB");

    let tgt_host = env::var("TARGET_ADDRESS").expect("TARGET_ADDRESS");
    let tgt_port = env::var("TARGET_PORT").unwrap_or_else(|_| "5432".into());
    let tgt_user = env::var("TARGET_USER").expect("TARGET_USER");
    let tgt_pass = env::var("TARGET_PASS").expect("TARGET_PASS");
    let tgt_db = env::var("TARGET_DB").expect("TARGET_DB");

    let source_table = env::var("SOURCE_TABLE").unwrap_or_else(|_| "os_open_uprn".into());

    let src = connect(&src_host, &src_port, &src_user, &src_pass, &src_db).await;
    let tgt = connect(&tgt_host, &tgt_port, &tgt_user, &tgt_pass, &tgt_db).await;

    // Fetch column names from the source table so COPY FROM targets only those
    // columns, regardless of any extra columns on the target.
    let col_rows = src
        .query(
            "SELECT column_name FROM information_schema.columns \
             WHERE table_schema = 'public' AND table_name = $1 \
             ORDER BY ordinal_position",
            &[&source_table],
        )
        .await
        .expect("column query failed");

    let columns: Vec<String> = col_rows.iter().map(|r| r.get(0)).collect();
    let col_list = columns.join(", ");

    println!("Copying {source_table} -> os_open_uprn via binary COPY...");

    // Stream binary COPY from source into an in-memory buffer.
    let copy_out_sql = format!(
        "COPY (SELECT * FROM public.{source_table}) TO STDOUT (FORMAT BINARY)"
    );
    let stream = src
        .copy_out(&copy_out_sql)
        .await
        .expect("COPY TO STDOUT failed");

    // Collect all chunks into a buffer.
    let mut buf = BytesMut::new();
    {
        use futures_util::TryStreamExt;
        let mut stream = std::pin::pin!(stream);
        while let Some(chunk) = stream.try_next().await.expect("stream error") {
            buf.extend_from_slice(&chunk);
        }
    }
    let data: Bytes = buf.freeze();

    // Stream binary data into target.
    let copy_in_sql = format!("COPY os_open_uprn ({col_list}) FROM STDIN (FORMAT BINARY)");
    let sink = tgt
        .copy_in(&copy_in_sql)
        .await
        .expect("COPY FROM STDIN failed");

    {
        use futures_util::SinkExt;
        let mut sink = std::pin::pin!(sink);
        sink.send(data).await.expect("sink send failed");
        sink.close().await.expect("sink close failed");
    }

    println!("Done.");
}
