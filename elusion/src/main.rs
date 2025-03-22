use elusion::prelude::*; 
use std::env;

#[tokio::main]
async fn main() -> ElusionResult<()> {
    let TARGET_USER = env::var("TARGET_USER").unwrap();
    let TARGET_PASS = env::var("TARGET_PASS").unwrap();
    let TARGET_DB = env::var("TARGET_DB").unwrap();
    let TARGET_ADDRESS = env::var("TARGET_ADDRESS").unwrap();
    
    let ORIGIN_USER = env::var("ORIGIN_USER").unwrap(); 
    let ORIGIN_ADDRESS = env::var("ORIGIN_ADDRESS").unwrap();
    let ORIGIN_PASS = env::var("ORIGIN_PASS").unwrap();
    let ORIGIN_DB = env::var("ORIGIN_DB").unwrap();

    let target_connection = format!("\
        Driver={{PostgreSQL UNICODE}};\
        Servername={};\
        Port=5433;\
        Database={};\
        UID={};\
        PWD={};", TARGET_ADDRESS, TARGET_DB, TARGET_USER, TARGET_PASS);

    let origin_connection = format!("\
        Driver={{PostgreSQL UNICODE}};\
        Servername={};\
        Port=5432;\
        Database={};\
        UID={};\
        PWD={};", ORIGIN_ADDRESS, ORIGIN_DB, ORIGIN_USER, ORIGIN_PASS);

    let sql_query = "SELECT * FROM os_open_uprn";
    let pg_df = CustomDataFrame::from_db(&origin_connection, sql_query).await?;
    let pg_res = pg_df.elusion("pg_res").await?;
    pg_res.display().await?;

    Ok(())
}
