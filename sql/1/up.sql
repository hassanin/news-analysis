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

CREATE OR REPLACE TYPE article_chunk_search_result AS (
    article_id INTEGER,
    chunk TEXT,
    chunk_id INTEGER,
    created_at TIMESTAMP,
    search_rank REAL
);
-- Create a stored procedure that retrieves article chunks based based on full text search on the body_tsvector
CREATE OR REPLACE FUNCTION search_article_chunks(search_term TEXT)
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
        WHERE ac.chunk_tsvector @@ query
    )
    SELECT article_id, chunk, chunk_id, created_at, search_rank
    FROM ranked_chunks
    ORDER BY search_rank DESC
    LIMIT 100;
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

ALTER TABLE article_chunk ADD COLUMN aritcle_title TEXT NOT NULL DEFAULT 'Unknown';



UPDATE article_chunk SET aritcle_title = a.title
FROM article a
WHERE a.id = article_id;

ALTER TABLE article ADD COLUMN president TEXT NOT NULL DEFAULT 'Unknown';
UPDATE article SET president = 'Biden';

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
CREATE OR REPLACE FUNCTION get_similar_chunks(embedding_vector vector(1536), num_chunks INTEGER)
RETURNS TABLE(article_id INTEGER, chunk TEXT, chunk_id INTEGER, article_title TEXT, created_at TIMESTAMP, distance FLOAT) AS $$
BEGIN
    RETURN QUERY
    SELECT ac.article_id, ac.chunk, ac.chunk_id, ac.article_title, ac.created_at, 
           1 - (ac.embedding <=> embedding_vector) AS distance
    FROM article_chunk ac
    ORDER BY (ac.embedding <=> embedding_vector) 
    LIMIT num_chunks;
END;
$$ LANGUAGE plpgsql;

-- 

