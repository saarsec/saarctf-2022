CREATE TABLE IF NOT EXISTS rds_databases (
    id integer PRIMARY KEY,
    dbname text NOT NULL UNIQUE,
    token text NOT NULL
);

INSERT OR REPLACE INTO rds_databases (id, dbname, token) VALUES (1, 'default', 'testtoken');

CREATE TABLE IF NOT EXISTS lambda_sites (
    id integer PRIMARY KEY,
    sitename text NOT NULL UNIQUE,
    token text NOT NULL
);

INSERT OR REPLACE INTO lambda_sites (id, sitename, token) VALUES (1, 'default', 'not-a-valid-sha256-hash');

CREATE TABLE IF NOT EXISTS featured_sites (
    id integer PRIMARY KEY,
    ts DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name text NOT NULL UNIQUE,
    feature text NOT NULL CHECK(feature = 'rds' OR feature = 'lambda' OR feature = 'cdn')
);
