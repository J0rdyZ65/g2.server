DROP TABLE IF EXISTS OAuth2;

CREATE TABLE IF NOT EXISTS OAuth2 (
    client_ip TEXT,
    client_hash TEXT,
    client_name TEXT,
    redirect_url TEXT,
    g2_server_client_id INTEGER,
    service_code TEXT,
    expire INTEGER,
    UNIQUE(client_ip, client_hash)
);
