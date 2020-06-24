DROP TABLE IF EXISTS OAuth2;

CREATE TABLE IF NOT EXISTS OAuth2 (
    client_ip TEXT,
    client_hash TEXT,
    client_name TEXT,
    g2_server_client_id INTEGER,
    service_name TEXT,
    service_author TEXT,
    expire INTEGER,
    UNIQUE(client_ip, client_name, client_hash, service_name)
);
