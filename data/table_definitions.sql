DROP TABLE IF EXISTS os_open_uprn_full;
CREATE TABLE os_open_uprn_full (
    uprn BIGINT NOT NULL,
    x_coordinate FLOAT8 NOT NULL,
    y_coordinate FLOAT8 NOT NULL,
    latitude FLOAT8 NOT NULL,
    longitude FLOAT8 NOT NULL
);