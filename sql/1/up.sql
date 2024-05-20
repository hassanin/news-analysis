-- Postgres
CREATE TABLE IF NOT EXISTS article (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    -- updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE article ADD COLUMN title_tsvector tsvector;
ALTER TABLE article ADD COLUMN body_tsvector tsvector;
ALTER TABLE article ADD COLUMN link_tsvector tsvector;

CREATE INDEX title_idx ON article USING GIN(title_tsvector);
CREATE INDEX body_idx ON article USING GIN(body_tsvector);
CREATE INDEX link_idx ON article USING GIN(link_tsvector);

UPDATE article 
SET title_tsvector = to_tsvector('english', title),
    body_tsvector = to_tsvector('english', body),
    link_tsvector = to_tsvector('english', link)
WHERE title_tsvector IS NULL
   OR body_tsvector IS NULL
   OR link_tsvector IS NULL;

-- UPDate article_chunk to set full text search
UPDATE article_chunk
SET chunk_tsvector = to_tsvector('english', chunk)
WHERE chunk_tsvector IS NULL;

CREATE OR REPLACE FUNCTION article_trigger() RETURNS trigger AS $$
begin
  new.title_tsvector := to_tsvector('english', new.title);
  new.body_tsvector := to_tsvector('english', new.body);
  new.link_tsvector := to_tsvector('english', new.link);
  return new;
end
$$ LANGUAGE plpgsql;

CREATE TRIGGER article_update BEFORE INSERT OR UPDATE
ON article FOR EACH ROW EXECUTE FUNCTION article_trigger();




SELECT COUNT(a.title) FROM article a
WHERE a.title_tsvector @@ to_tsquery('english', 'Egypt')
   OR a.body_tsvector @@ to_tsquery('english', 'Egypt')
   OR a.link_tsvector @@ to_tsquery('english', 'Egypt');



SELECT a.link, ts_rank(title_tsvector, 'Israel') AS title_rank,
          ts_rank(body_tsvector, 'Israel') AS body_rank,
          ts_rank(link_tsvector, 'Israel') AS link_rank
FROM article a, to_tsquery('english', 'Israel') query
WHERE a.title_tsvector @@ query
   OR a.body_tsvector @@ query
   OR a.link_tsvector @@ query
ORDER BY title_rank + body_rank + link_rank DESC;


SELECT * FROM (
    SELECT article.link, 
           ts_rank(title_tsvector, query) AS title_rank,
           ts_rank(body_tsvector, query) AS body_rank,
           ts_rank(link_tsvector, query) AS link_rank
    FROM article, websearch_to_tsquery('english', 'Gaza Death toll') query
    WHERE title_tsvector @@ query
       OR body_tsvector @@ query
       OR link_tsvector @@ query
) AS ranked_articles
ORDER BY title_rank + body_rank + link_rank DESC;


SELECT COUNT(*) FROM (
    SELECT 1
    FROM article, websearch_to_tsquery('english', 'Gaza Death toll') query
    WHERE title_tsvector @@ query
       OR body_tsvector @@ query
       OR link_tsvector @@ query
) AS ranked_articles;


SELECT cfgname FROM pg_ts_config;
--array aggreagre the reults
SELECT array_agg(cfgname) FROM pg_ts_config;

-- https://xata.io/blog/postgres-full-text-search-engine
-- https://learn.microsoft.com/en-us/azure/search/search-lucene-query-architecture#stage-2-lexical-analysis


CREATE TYPE article_rank_type AS (
    id INT,
    title TEXT,
    link TEXT,
    body TEXT,
    created_at TIMESTAMP,
    total_rank REAL
);

CREATE OR REPLACE FUNCTION search_articles(search_term TEXT)
RETURNS SETOF article_rank_type AS $$
BEGIN
    RETURN QUERY
    WITH ranked_articles AS (
        SELECT article.id,
               article.title,
               article.link,
               article.body,
               article.created_at,
               ts_rank(title_tsvector, query) AS title_rank,
               ts_rank(body_tsvector, query) AS body_rank,
               ts_rank(link_tsvector, query) AS link_rank
        FROM article, websearch_to_tsquery('english', search_term) query
        WHERE title_tsvector @@ query
           OR body_tsvector @@ query
           OR link_tsvector @@ query
    )
    SELECT id, title, link, body, created_at, (title_rank + body_rank + link_rank) AS total_rank
    FROM ranked_articles
    ORDER BY total_rank DESC
    LIMIT 100;
END;
$$ LANGUAGE plpgsql;

CREATE TYPE article_chunk_search_result AS (
    article_id INTEGER,
    chunk TEXT,
    chunk_id INTEGER,
    created_at TIMESTAMP,
    search_rank REAL
);
-- Create a stored procedure that retrieves article chunks based based on full text search on the body_tsvector
CREATE OR REPLACE FUNCTION search_article_chunks(search_term TEXT, num_chunks INTEGER, opt_month INTEGER DEFAULT NULL, opt_year INTEGER DEFAULT NULL)
RETURNS SETOF article_chunk_search_result AS $$
BEGIN
    RETURN QUERY
    WITH ranked_chunks AS (
        SELECT ac.article_id,
               ac.chunk,
               ac.chunk_id,
               ac.created_at,
               ts_rank(ac.chunk_tsvector, query) AS search_rank
        FROM article_chunk ac, websearch_to_tsquery('english', search_term) query
        WHERE ac.chunk_tsvector @@ query AND
              (opt_month IS NULL OR EXTRACT(MONTH FROM ac.created_at) = opt_month) AND
              (opt_year IS NULL OR EXTRACT(YEAR FROM ac.created_at) = opt_year)
    )
    SELECT article_id, chunk, chunk_id, created_at, search_rank
    FROM ranked_chunks
    ORDER BY search_rank DESC
    LIMIT num_chunks;
END;
$$ LANGUAGE plpgsql;


-- Create a stored procedure that retrieves article chunks based based on full text search on the body_tsvector
CREATE OR REPLACE FUNCTION search_article_summaries(search_term TEXT, num_chunks INTEGER, opt_month INTEGER DEFAULT NULL, opt_year INTEGER DEFAULT NULL)
RETURNS SETOF article_chunk_search_result AS $$
BEGIN
    RETURN QUERY
    WITH ranked_chunks AS (
        SELECT a.id,
               a.summary,
               0,
               a.created_at,
               ts_rank(a.summary_tsvector, query) AS search_rank
        FROM article a, websearch_to_tsquery('english', search_term) query
        WHERE a.summary_tsvector @@ query AND
              (opt_month IS NULL OR EXTRACT(MONTH FROM a.created_at) = opt_month) AND
              (opt_year IS NULL OR EXTRACT(YEAR FROM a.created_at) = opt_year)
    )
    SELECT article_id, chunk, chunk_id, created_at, search_rank
    FROM ranked_chunks
    ORDER BY search_rank DESC
    LIMIT num_chunks;
END;
$$ LANGUAGE plpgsql;

-- use database url to generate models
-- sqlacodegen postgresql://postgres:postgres@localhost:5432/newsanalysis > models.py

-- extract date from link
UPDATE article
SET created_at = TO_TIMESTAMP(SUBSTRING(link FROM '(\d{4}/\d{2}/\d{2})'), 'YYYY/MM/DD')

-- RENAME COLUMN aritcle_title TO article_title;
ALTER TABLE article_chunk RENAME COLUMN aritcle_title TO article_title;

CREATE EXTENSION vector;
-- 1536 is the size of the embeddings


-- Creating a table for the chunks with embeddings
CREATE TABLE IF NOT EXISTS article_chunk (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    chunk TEXT NOT NULL,
    chunk_id INTEGER NOT NULL,
    -- embedding is a 1D array of floats with a size of 512
    embedding vector(1536) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE article_chunk ADD COLUMN chunk_tsvector tsvector;
CREATE INDEX chunk_idx ON article_chunk USING GIN(chunk_tsvector);

UPDATE article_chunk
SET chunk_tsvector = to_tsvector('english', chunk)
WHERE chunk_tsvector IS NULL;

ALTER TABLE article_chunk ADD COLUMN article_title TEXT NOT NULL DEFAULT 'Unknown';



UPDATE article_chunk SET article_title = a.title
FROM article a
WHERE a.id = article_id;

ALTER TABLE article ADD COLUMN president TEXT NOT NULL DEFAULT 'Unknown';
UPDATE article SET president = 'Biden';

ALTER TABLE article_chunk ADD COLUMN president TEXT NOT NULL DEFAULT 'Unknown';
UPDATE article_chunk SET president = 'Biden';

UPDATE article
SET body = REGEXP_REPLACE(body, E'(\r\n|\r|\n)+', ' ', 'g')
WHERE president = 'Trump';
--REGEXP_REPLACE(content, E'(\r\n|\r|\n)+', ' ', 'g');

SELECT a.president, COUNT(1)
FROM article a
GROUP BY a.president;

UPDATE article
SET created_at = TO_TIMESTAMP(SUBSTRING(link FROM '(\d{4}/\d{2}/\d{2})'), 'YYYY/MM/DD')
WHERE link ~ '\d{4}/\d{2}/\d{2}';


WItH search_results AS(
    SELECT * FROM search_articles('China')
)
-- GROUP Search results by year of created_at
SELECT EXTRACT(YEAR FROM created_at) AS year, COUNT(1) AS count
FROM search_results
WHERE  created_at < CURRENT_DATE - INTERVAL '7 days'
GROUP BY year
ORDER BY year;

-- Create a Stored Procedure that retrieves article chunks based on the embedding ector using cosine similarity
-- metric and should take a paramter of how many chunks to return, return only the article_id, chunk, and chunk_id
-- CREATE OR REPLACE FUNCTION get_similar_chunks(embedding_vector vector(1536), num_chunks INTEGER)
-- RETURNS TABLE(article_id INTEGER, chunk TEXT, chunk_id INTEGER, article_title TEXT, created_at TIMESTAMP, distance FLOAT) AS $$
-- BEGIN
--     RETURN QUERY
--     SELECT ac.article_id, ac.chunk, ac.chunk_id, ac.article_title, ac.created_at, 
--            1 - (ac.embedding <=> embedding_vector) AS distance
--     FROM article_chunk ac
--     WHERE ac.created_at < '2024-01-01'
--     ORDER BY  (ac.embedding <=> embedding_vector), ac.created_at DESC
--     LIMIT num_chunks;
-- END;
-- $$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_similar_chunks(embedding_vector vector, num_chunks INTEGER, opt_month INTEGER DEFAULT NULL, opt_year INTEGER DEFAULT NULL)
RETURNS TABLE(article_id INTEGER, chunk TEXT, chunk_id INTEGER, article_title TEXT, created_at TIMESTAMP, distance FLOAT, score FLOAT, cosine_distance FLOAT) AS $$
DECLARE
  max_date TIMESTAMP;
  min_date TIMESTAMP;
  date_range FLOAT;
BEGIN
  -- Get the maximum and minimum created_at dates from article_chunk
  SELECT MAX(ac.created_at), MIN(ac.created_at) INTO max_date, min_date FROM article_chunk ac;
  -- Calculate the total date range to normalize date factor, avoid division by zero
  IF min_date = max_date THEN
    date_range := 1; -- Assign a default value to avoid division by zero
  ELSE
    date_range := EXTRACT(EPOCH FROM max_date - min_date);
  END IF;

  -- Return query with combined similarity (distance) and score, including date factor
  RETURN QUERY
  SELECT
    ac.article_id,
    ac.chunk,
    ac.chunk_id,
    ac.article_title,
    ac.created_at,
    1 - (ac.embedding <=> embedding_vector) AS distance, -- Calculate distance using the pgvector distance operator
    (
      0.8 * (1 - (ac.embedding <=> embedding_vector)) + -- Weighted cosine distance
      0.0 * (1 - (EXTRACT(EPOCH FROM current_date - ac.created_at) / date_range)) -- Weighted normalized date factor, current_date is a psql internal function
    ) AS score,
    ac.embedding <=> embedding_vector AS cosine_distance
  FROM article_chunk ac
  WHERE  ac.embedding <=> embedding_vector < 0.2 AND -- Filter out chunks with cosine distance less than 0.2
        (opt_month IS NULL OR EXTRACT(MONTH FROM ac.created_at) = opt_month) AND -- Filter by month if provided
        (opt_year IS NULL OR EXTRACT(YEAR FROM ac.created_at) = opt_year) -- Filter by year if provided
  ORDER BY score DESC
  LIMIT num_chunks;
END;
$$ LANGUAGE plpgsql;
-- 

CREATE OR REPLACE FUNCTION vector_search_summary(embedding_vector vector, num_chunks INTEGER, opt_month INTEGER DEFAULT NULL, opt_year INTEGER DEFAULT NULL)
RETURNS TABLE(article_id INTEGER, chunk TEXT, article_title TEXT, created_at TIMESTAMP, distance FLOAT, score FLOAT, cosine_distance FLOAT) AS $$
DECLARE
  max_date TIMESTAMP;
  min_date TIMESTAMP;
  date_range FLOAT;
BEGIN
  -- Get the maximum and minimum created_at dates from article_chunk
  SELECT MAX(ac.created_at), MIN(ac.created_at) INTO max_date, min_date FROM article_chunk ac;
  -- Calculate the total date range to normalize date factor, avoid division by zero
  IF min_date = max_date THEN
    date_range := 1; -- Assign a default value to avoid division by zero
  ELSE
    date_range := EXTRACT(EPOCH FROM max_date - min_date);
  END IF;

  -- Return query with combined similarity (distance) and score, including date factor
  RETURN QUERY
  SELECT
    a.id,
    a.summary,
    a.title,
    a.created_at,
    1 - (a.summary_embedding <=> embedding_vector) AS distance, -- Calculate distance using the pgvector distance operator
    (
      0.8 * (1 - (a.summary_embedding <=> embedding_vector)) + -- Weighted cosine distance
      0.2 * (1 - (EXTRACT(EPOCH FROM current_date - a.created_at) / date_range)) -- Weighted normalized date factor, current_date is a psql internal function
    ) AS score,
    a.summary_embedding <=> embedding_vector AS cosine_distance
  FROM article a
  WHERE  a.summary_embedding <=> embedding_vector < 0.2 AND -- Filter out chunks with cosine distance less than 0.2
        (opt_month IS NULL OR EXTRACT(MONTH FROM a.created_at) = opt_month) AND -- Filter by month if provided
        (opt_year IS NULL OR EXTRACT(YEAR FROM a.created_at) = opt_year) -- Filter by year if provided
  ORDER BY score DESC
  LIMIT num_chunks;
END;
$$ LANGUAGE plpgsql;

-- For each month of the year since 2011 till 2023, count the number of articles, and the number
-- of characters in each month
WITH article_counts AS (
    SELECT EXTRACT(YEAR FROM created_at) AS year,
           EXTRACT(MONTH FROM created_at) AS month,
           COUNT(1) AS count,
           SUM(LENGTH(body)/4.0) AS total_chars
    FROM article
    WHERE created_at < '2024-01-01' AND created_at > '2011-01-01'
    GROUP BY year, month
    ORDER BY year, month
) 
SELECT year, month, count, total_chars
FROM article_counts;

WITH article_counts AS (
    SELECT EXTRACT(YEAR FROM created_at) AS year,
           EXTRACT(MONTH FROM created_at) AS month,
           COUNT(1) AS count,
           SUM(LENGTH(summary)/4.0) AS total_chars
    FROM article
    WHERE created_at < '2024-01-01' AND created_at > '2011-01-01'
    GROUP BY year, month
    ORDER BY year, month
) 
SELECT year, month, count, total_chars
FROM article_counts;

ALTER TABLE article add COLUMN summary TEXT NOT NULL DEFAULT 'Unknown';

ALTER TABLE article ADD COLUMN summary_tsvector tsvector;
CREATE INDEX summary_idx ON article USING GIN(summary_tsvector);
UPDATE article 
SET summary_tsvector = to_tsvector('english', summary)
WHERE summary_tsvector IS NULL;

-- See articles which has egypt in the summary tsvector
-- Take the first 50 chars of the title, display the year and month, order by year and month
SELECT COUNT(1) as total_articles, 
EXTRACT(YEAR FROM created_at) AS year, 
EXTRACT(MONTH FROM created_at) AS month
FROM article
WHERE summary_tsvector @@ to_tsquery('english', 'China')
GROUP BY year, month
ORDER BY year, month;


-- def get_summary_article_results(search_term: str, month:int, year:int) -> list[ArticleSummarySearchResult]:
SELECT a.title, a.summary, a.created_at
FROM article a
WHERE a.summary_tsvector @@ websearch_to_tsquery('english', 'China')
AND EXTRACT(YEAR FROM a.created_at) = 2023
AND EXTRACT(MONTH FROM a.created_at) = 1
ORDER BY a.created_at DESC
LIMIT 100;

ALTER TABLE article ADD COLUMN summary_embedding vector(1536);


CREATE OR REPLACE FUNCTION hybrid_vector_fulltext_search(
    search_term TEXT,
    embedding_vector VECTOR,
    num_chunks INTEGER = 10,
    rrf_k INTEGER = 60,
    full_text_weight float = 1,
    vector_weight float = 1,
    opt_month INTEGER DEFAULT NULL,
    opt_year INTEGER DEFAULT NULL
)
RETURNS TABLE(article_id INTEGER, chunk_id INTEGER, chunk TEXT, created_at TIMESTAMP, combined_score FLOAT) AS $$
BEGIN
    -- Temporary table to store full text search results with RRF scores
    CREATE TEMP TABLE full_text_results AS
    SELECT *, 
           row_number() OVER (ORDER BY search_rank DESC) AS rank
    FROM
        search_article_chunks(search_term, num_chunks * 2, opt_month, opt_year);

    -- Temporary table to store vector search results with RRF scores
    CREATE TEMP TABLE vector_search_results AS
    SELECT *,
           row_number() OVER (ORDER BY score DESC) AS rank
    FROM
        get_similar_chunks(embedding_vector, num_chunks * 2, opt_month, opt_year);

    -- Combining results from full text and vector search using RRF
    RETURN QUERY
    SELECT
        coalesce(ft.article_id, vs.article_id) AS article_id,
        coalesce(ft.chunk_id, vs.chunk_id) AS chunk_id,
        coalesce(ft.chunk, vs.chunk) AS chunk,
        coalesce(ft.created_at, vs.created_at) AS created_at,
        (coalesce(1.0/ (rrf_k + ft.rank),0.0) * full_text_weight + coalesce(1.0/ (rrf_k + vs.rank),0.0) * vector_weight )::double precision AS combined_score
        -- (1.0 / (rrf_k + coalesce(ft.rank, rrf_k * 2))) + (1.0 / (rrf_k + coalesce(vs.rank, rrf_k * 2)))::double precision AS combined_score
    FROM
        full_text_results ft
    FULL OUTER JOIN
        vector_search_results vs ON ft.article_id = vs.article_id AND ft.chunk_id = vs.chunk_id
    ORDER BY
        combined_score DESC
    LIMIT num_chunks;

    -- Cleanup temporary tables
    DROP TABLE full_text_results;
    DROP TABLE vector_search_results;
END;
$$ LANGUAGE plpgsql;

CREATE INDEX ON article_chunk USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
-- CREATE INDEX ON items USING hnsw (embedding vector_l2_ops) WITH (m = 16, ef_construction = 64);

-- Aggregate artictles by year
SELECT EXTRACT(YEAR FROM created_at) AS year, COUNT(1) AS count
FROM article
GROUP BY year
ORDER BY year;

SELECT EXTRACT(YEAR FROM created_at) AS year, COUNT(1) AS count
FROM article_chunk
GROUP BY year
ORDER BY year;