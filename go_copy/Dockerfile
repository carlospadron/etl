# ── build stage ──────────────────────────────────────────────────────────────
FROM golang:1.22-bookworm AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download && go mod verify

COPY main.go .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o go_copy .

# ── runtime stage ─────────────────────────────────────────────────────────────
FROM scratch

COPY --from=builder /app/go_copy /go_copy

ENTRYPOINT ["/go_copy"]
