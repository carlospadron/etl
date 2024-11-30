import org.apache.spark.sql.{SparkSession, DataFrame}

@main def etl(): Unit =
  val spark = SparkSession.builder()
      .appName("Scals/spark ETL")
      .config("spark.master", "local[*]")
      .getOrCreate()

  val db_user_terra = sys.env("data_uploads_user")
  val db_password_terra = sys.env("data_uploads_pass_staging")
  val db_name_terra = sys.env("db_name")
  val db_address_terra = sys.env("db_address_stag")

  val sf_user = sys.env("sf_user")
  val sf_db_address = sys.env("sf_db_address")
  val sf_pass = sys.env("sf_pass")
  val sf_db_name = sys.env("sf_db_name")

  // Database connection properties
  val url_terra = s"jdbc:postgresql://$db_address_terra/$db_name_terra"
  val url_sf = s"jdbc:postgresql://$sf_db_address/$sf_db_name"

  // config
  val table_sf = "public_sf_legacy.asset_legacy"
  val table_terra = "public_sf_legacy.asset_legacy"
  val query = s"SELECT * FROM $table_sf"

  // Read data from PostgreSQL into a DataFrame
  println("Reading data from PostgreSQL into a DataFrame")
  val df: DataFrame = spark.read
    .format("jdbc")
    .option("url", url_sf)
    .option("query", query)
    .option("user", sf_user)
    .option("password", sf_pass)
    .option("fetchsize", "100000")
    .load()

  // Show the DataFrame
  //df.show()

  // Write the DataFrame to another PostgreSQL table
  println("Writing the DataFrame to another PostgreSQL table")

  // insert mode that is very slow but database agnostic
  df.repartition(20)
    .write
    .mode("overwrite") // append/overwrite
    .format("jdbc")
    .option("url", url_terra)
    .option("dbtable", table_terra)
    .option("user", db_user_terra)
    .option("password", db_password_terra)
    .option("batchsize", "10000")
    .option("truncate", "true")
    .save() 

  // Stop the Spark session
  spark.stop()

  println("ETL job completed")