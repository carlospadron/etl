import org.apache.spark.sql.{SparkSession, DataFrame}

@main def etl(): Unit =
  val spark = SparkSession.builder()
      .appName("Scals/spark ETL")
      .config("spark.master", "local[*]")
      .getOrCreate()

  val TARGET_USER = sys.env("TARGET_USER")
  val TARGET_PASS = sys.env("TARGET_PASS")
  val TARGET_DB = sys.env("TARGET_DB")
  val TARGET_ADDRESS = sys.env("TARGET_ADDRESS")

  val ORIGIN_USER = sys.env("ORIGIN_USER")
  val ORIGIN_ADDRESS = sys.env("ORIGIN_ADDRESS")
  val ORIGIN_PASS = sys.env("ORIGIN_PASS")
  val ORIGIN_DB = sys.env("ORIGIN_DB")

  // Database connection properties
  val url_target = s"jdbc:postgresql://$TARGET_ADDRESS/$TARGET_DB"
  val url_origin = s"jdbc:postgresql://$ORIGIN_ADDRESS/$ORIGIN_DB"

  // config
  val table_origin = "public.os_open_uprn"
  val table_target = "os_open_uprn"
  val query = s"SELECT * FROM $table_origin"

  // Read data from PostgreSQL into a DataFrame
  println("Reading data from PostgreSQL into a DataFrame")
  val df: DataFrame = spark.read
    .format("jdbc")
    .option("url", url_origin)
    .option("query", query)
    .option("user", ORIGIN_USER)
    .option("password", ORIGIN_PASS)
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
    .option("url", url_target)
    .option("dbtable", table_target)
    .option("user", TARGET_USER)
    .option("password", TARGET_PASS)
    .option("batchsize", "10000")
    .option("truncate", "true")
    .save() 

  // Stop the Spark session
  spark.stop()

  println("ETL job completed")