
go:
	go run main.go

python:
	uv run main.py

rust:
	cargo run -- --workers 2 --port 8005

js:
	node main.js