psql -d postgres -f table_definitions.sql 
psql -d postgres -c "\copy os_open_uprn_full from 'osopenuprn_202502.csv' with csv header"
psql -d postgres -c "select * into os_open_uprn from os_open_uprn limit 20000000"