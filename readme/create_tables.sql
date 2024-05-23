SET TRANSACTION READ WRITE;

CREATE TABLE IF NOT EXISTS product_read_history (
	asin text,
	read_time timestamp,
	image_variations json,
	listing_price float,
	is_active boolean,
	merchant text,
	PRIMARY KEY (asin, read_time)
);

CREATE TABLE IF NOT EXISTS product_read_changes (
	asin text,
	read_time timestamp,
	image_variations json,
	listing_price float,
	is_active boolean,
	merchant text,
	PRIMARY KEY (asin, read_time)
);

CREATE TABLE IF NOT EXISTS ab_test_runs (
	run_id serial PRIMARY KEY NOT NULL,
	test_id int,
	run_time timestamp,
	feed_id bigint,
	variation text,
	merchant text
);

CREATE TABLE IF NOT EXISTS merchants (
	merchant_id serial PRIMARY KEY NOT NULL,
	lwa_client_secret text,
	lwa_app_id text,
	sp_api_secret_key text,
	sp_api_role_arn text,
	sp_api_refresh_token text,
	sp_api_access_key text,
	merchant text
);

SELECT
	table_name
FROM
	information_schema.tables
WHERE
	table_schema = 'public'
	AND table_type = 'BASE TABLE';
