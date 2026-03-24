package main

import (
	"bytes"
	"context"
	"fmt"
	"os"
	"strings"

	"github.com/jackc/pgx/v5"
)

func mustEnv(key string) string {
	v := os.Getenv(key)
	if v == "" {
		fmt.Fprintf(os.Stderr, "missing required env var: %s\n", key)
		os.Exit(1)
	}
	return v
}

func envOr(key, fallback string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return fallback
}

func connect(ctx context.Context, host, port, user, password, dbname string) *pgx.Conn {
	dsn := fmt.Sprintf("postgres://%s:%s@%s:%s/%s", user, password, host, port, dbname)
	conn, err := pgx.Connect(ctx, dsn)
	if err != nil {
		fmt.Fprintf(os.Stderr, "connect to %s:%s/%s failed: %v\n", host, port, dbname, err)
		os.Exit(1)
	}
	return conn
}

func main() {
	ctx := context.Background()

	srcHost := mustEnv("ORIGIN_ADDRESS")
	srcPort := envOr("ORIGIN_PORT", "5432")
	srcUser := mustEnv("ORIGIN_USER")
	srcPass := mustEnv("ORIGIN_PASS")
	srcDB := mustEnv("ORIGIN_DB")

	tgtHost := mustEnv("TARGET_ADDRESS")
	tgtPort := envOr("TARGET_PORT", "5432")
	tgtUser := mustEnv("TARGET_USER")
	tgtPass := mustEnv("TARGET_PASS")
	tgtDB := mustEnv("TARGET_DB")

	sourceTable := envOr("SOURCE_TABLE", "os_open_uprn")

	src := connect(ctx, srcHost, srcPort, srcUser, srcPass, srcDB)
	defer src.Close(ctx)

	tgt := connect(ctx, tgtHost, tgtPort, tgtUser, tgtPass, tgtDB)
	defer tgt.Close(ctx)

	// Fetch column names from the source table so COPY FROM targets only those
	// columns, regardless of any extra columns on the target.
	rows, err := src.Query(ctx,
		`SELECT column_name FROM information_schema.columns
		 WHERE table_schema = 'public' AND table_name = $1
		 ORDER BY ordinal_position`,
		sourceTable,
	)
	if err != nil {
		fmt.Fprintf(os.Stderr, "column query failed: %v\n", err)
		os.Exit(1)
	}
	var columns []string
	for rows.Next() {
		var col string
		if err := rows.Scan(&col); err != nil {
			fmt.Fprintf(os.Stderr, "scan error: %v\n", err)
			os.Exit(1)
		}
		columns = append(columns, col)
	}
	rows.Close()
	colList := strings.Join(columns, ", ")

	fmt.Printf("Copying %s -> os_open_uprn via binary COPY...\n", sourceTable)

	// Read binary COPY data from source into an in-memory buffer.
	var buf bytes.Buffer
	copyOutSQL := fmt.Sprintf(
		"COPY (SELECT * FROM public.%s) TO STDOUT (FORMAT BINARY)", sourceTable,
	)
	_, err = src.PgConn().CopyTo(ctx, &buf, copyOutSQL)
	if err != nil {
		fmt.Fprintf(os.Stderr, "COPY TO STDOUT failed: %v\n", err)
		os.Exit(1)
	}

	// Write binary COPY data to target.
	copyInSQL := fmt.Sprintf("COPY os_open_uprn (%s) FROM STDIN (FORMAT BINARY)", colList)
	_, err = tgt.PgConn().CopyFrom(ctx, &buf, copyInSQL)
	if err != nil {
		fmt.Fprintf(os.Stderr, "COPY FROM STDIN failed: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Done.")
}
