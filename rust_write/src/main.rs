use postgres::{Client, NoTls};
use polars::datatypes::AnyValue;
// use chrono::{NaiveDate, NaiveDateTime};

fn connect_to_postgres(
    db_user: String, 
    db_password: String,
    TARGET_DB: String,
    db_address: String
) -> Client {

    // Connect to the PostgreSQL database
    Client::connect(
        &format!(
            "host={} user={} password={} dbname={}",
            db_address, db_user, db_password, TARGET_DB
        ),
        NoTls,
    ).unwrap()
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Set the schema and table
    let schema_origin = "public_origin_legacy";    
    let table_origin = "asset_legacy";
    let table_target = "public_origin_legacy.asset_legacy";

    // Get env vars
    let TARGET_USER = std::env::var("TARGET_USER")?;
    let TARGET_PASS = std::env::var("TARGET_PASS")?;
    let TARGET_DB = std::env::var("TARGET_DB")?;
    let TARGET_ADDRESS = std::env::var("db_TARGET_ADDRESSaddress_target")?;

    let ORIGIN_USER = std::env::var("ORIGIN_USER")?;
    let ORIGIN_ADDRESS = std::env::var("ORIGIN_ADDRESS")?;
    let ORIGIN_PASS = std::env::var("ORIGIN_PASS")?;
    let ORIGIN_DB = std::env::var("ORIGIN_DB")?;    

    // Connect to the PostgreSQL database
    let terra_client = connect_to_postgres(
        TARGET_USER,
        TARGET_PASS,
        TARGET_DB,
        TARGET_ADDRESS
    );

    let mut sf_client = connect_to_postgres(
        ORIGIN_USER, 
        ORIGIN_PASS, 
        ORIGIN_DB, 
        ORIGIN_ADDRESS
    );

    // // Query to get the schema information
    // let schema_query = format!("
    //     SELECT column_name, data_type
    //     FROM information_schema.columns
    //     WHERE table_schema = '{}' AND table_name = '{}'", 
    //     schema_origin,
    //     table_origin
    // );
    // let schema_rows = sf_client.query(&schema_query, &[])?;

    // // Extract column names and types
    // let columns: Vec<&str> = schema_rows
    //     .iter()
    //     .map(|row| row.get("column_name"))
    //     .collect();
    // let column_types: Vec<&str> = schema_rows
    //     .iter()
    //     .map(|row| row.get("data_type"))
    //     .collect();

    // Query to fetch data
    let query = format!("SELECT * FROM {}.{} limit 100", schema_origin, table_origin);   
    let rows = sf_client.query(&query, &[])?;

    // Iterate over rows and columns to get the data
    // let data: Vec<Vec<AnyValue>> = rows
    //     .iter()
    //     .map(|row|
    //         column_types
    //         .iter()
    //         .enumerate()
    //         .map(|(i, col_type)| {
    //             match *col_type {                 
    //                 "text" | "varchar" => match row.get(i) {
    //                     Some(v) => AnyValue::String(v),
    //                     None => AnyValue::Null,
    //                 },
    //                 "int4" | "int" => match row.get(i) {
    //                     Some(v) => AnyValue::Int32(v),
    //                     None => AnyValue::Null,
                        
    //                 },                 
    //                 "bigint" => match row.get(i) {
    //                     Some(v) => AnyValue::Int64(v),
    //                     None => AnyValue::Null,
                        
    //                 },
    //                 "boolean" => match row.get(i) {
    //                     Some(v) => AnyValue::Boolean(v),
    //                     None => AnyValue::Null,
                        
    //                 },
    //                 // "date" => AnyValue::Date(DateTime::parse_from_str(row.get(i)),
    //                 "double precision" | "float8" => match row.get(i) {
    //                     Some(v) => AnyValue::Float64(v),
    //                     None => AnyValue::Null,
                        
    //                 },
    //                 "numeric" => match row.get(i) {
    //                     Some(v) => AnyValue::Float64(Decimal::from_str(v).unwrap().to_f64().unwrap()),
    //                     None => AnyValue::Null,
                        
    //                 },
    //                 // "timestamp with time zone" | "timestamp without time zone" => {
    //                 //     AnyValue::Datetime(row.get::<_, NaiveDateTime>(i).and_utc().timestamp_millis(), TimeUnit::Milliseconds, None)
    //                 // }
    //                 _ => AnyValue::Null,
    //             }
    //         })
    //         .collect()
    //     )
    //     .collect();

    // print!("{:?}", data);
    // Create a Polars DataFrame
    // let df = DataFrame::new(
    //     columns
    //         .iter()
    //         .zip(data.into_iter())
    //         .map(|(name, col)| Series::new(name, col))
    //         .collect::<Result<Vec<_>, _>>()?,
    // )?;

    // // Print the DataFrame
    // println!("{:?}", df);
    Ok(())
}