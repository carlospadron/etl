# Go COPY (`go_copy`)

Reads from source PostgreSQL using `COPY … TO STDOUT (FORMAT BINARY)` and writes to the target using `COPY … FROM STDIN (FORMAT BINARY)`, buffering in memory via `pgx/v5`.

This is the Go equivalent of `psycopg2_copy` — the same binary COPY protocol, no ORM, no serialisation overhead. The final image is built `FROM scratch` (a static binary with no base OS), giving the smallest possible image size.
