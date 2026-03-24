# Rust COPY (`rust_copy`)

Reads from source PostgreSQL using `COPY … TO STDOUT (FORMAT BINARY)` and writes to the target using `COPY … FROM STDIN (FORMAT BINARY)`, buffering in memory via `tokio-postgres`.

This is the Rust equivalent of `psycopg2_copy` — the same binary COPY protocol, no ORM, no serialisation overhead.
