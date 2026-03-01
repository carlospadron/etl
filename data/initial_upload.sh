psql -d postgres -f table_definitions.sql 
CSV_FILE=$(ls osopenuprn_*.csv 2>/dev/null | head -1)
if [ -z "${CSV_FILE}" ]; then
    echo "Error: No CSV file found matching osopenuprn_*.csv"
    exit 1
fi
echo "Using CSV file: ${CSV_FILE}"
psql -d postgres -c "\copy os_open_uprn_full from '${CSV_FILE}' with csv header"
psql -d postgres -c "drop table os_open_uprn"
psql -d postgres -c "select * into os_open_uprn from os_open_uprn_full"
#psql -d postgres -c "select * into os_open_uprn from os_open_uprn_full limit 2000000"