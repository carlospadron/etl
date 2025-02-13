psql -d postgres -f table_definitions.sql 
psql -d postgres -c "\copy os_open_uprn from 'osopenuprn_202502.csv' with csv header"