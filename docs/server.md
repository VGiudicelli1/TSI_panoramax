# Server

## Docker

2 containers are running together to serve the database:
- postgresql
- pgadmin (for DEV)

To start:
```
git checkout server
cd server_postgres
docker compose up -d
```

## Ngrok (DEV: not on git)

WARNING : DO NOT SHARE CREDENTIALS (token or forwardings) ON GIT

Used to allow remote access to database

get your config file with `ngrok config check`

edit your congig file with the content in `branch:server&file:server_postgres/config_ngrok.yml` with adding your token

start forwarding with `ngrok start postgres pgadmin`

You can access database remotly with the instructions displayed (lines `Forwarding`)

```
...
Forwarding     tcp://{postgres_ip}:{postgres_port} -> localhost:5432
Forwarding     {pgadmin_url} -> http://localhost:5050
...
```

Connect to postgres:
`psql -h {postgres_ip} -p {postgres_port} -U postgres -d postgres`

Connect to pgadmin with the url `pgadmin_url`
