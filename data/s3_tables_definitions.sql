--Use the following statement to create a table in your S3 Table bucket.
CREATE TABLE `os`.open_uprn (
    uprn BIGINT,
    x_coordinate FLOAT,
    y_coordinate FLOAT,
    latitude FLOAT,
    longitude FLOAT
)
PARTITIONED BY (uprn)
TBLPROPERTIES ('table_type' = 'iceberg')

CREATE EXTERNAL TABLE IF NOT EXISTS `os`.open_uprn_external (
    uprn BIGINT,
    x_coordinate FLOAT,
    y_coordinate FLOAT,
    latitude FLOAT,
    longitude FLOAT
)
STORED AS PARQUET
LOCATION 's3://your-bucket-name/path-to-data/'
TBLPROPERTIES ('table_type' = 'iceberg');

INSERT INTO `os`.open_uprn
SELECT *
FROM `os`.open_uprn_external
WHERE uprn IS NOT NULL;