DROP TABLE IF EXISTS urls;

CREATE TABLE urls (
id SERIAL PRIMARY KEY,
name VARCHAR(255) UNIQUE NOT NULL,
created_at TIMESTAMP

);

DROP TABLE IF EXISTS url_checks;

CREATE TABLE url_checks (
id SERIAL PRIMARY KEY,
url_id INT,
status_code INT,
h1 VARCHAR(255),
title VARCHAR(255),
description TEXT,
created_at TIMESTAMP
);

