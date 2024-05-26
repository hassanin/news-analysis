CREATE TABLE IF NOT EXISTS article (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    body TEXT NOT NULL,
    author TEXT , -- can be null if the author(s) is not known
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    -- updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- add a tsvector column to store the lexigrams of the article title and body
ALTER TABLE article ADD COLUMN body_tsvector tsvector;
ALTER TABLE article ADD COLUMN title_tsvector tsvector;
-- create a GIN index on the tsvector column
CREATE INDEX article_body_tsvector_idx ON article USING GIN(body_tsvector);
CREATE INDEX article_title_tsvector_idx ON article USING GIN(title_tsvector);
-- populate the tsvector column with the lexigrams of the article title and body
UPDATE article SET body_tsvector = to_tsvector('english', body);
UPDATE article SET title_tsvector = to_tsvector('english',title);

-- Trigger function to update the tsvector column when the article title or body is updated
CREATE OR REPLACE FUNCTION article_trigger() RETURNS trigger AS $$
begin
  new.title_tsvector := to_tsvector('english', new.title);
  new.body_tsvector := to_tsvector('english', new.body);
  return new;
end
$$ LANGUAGE plpgsql;

CREATE TRIGGER article_update BEFORE INSERT OR UPDATE
ON article FOR EACH ROW EXECUTE FUNCTION article_trigger();

CREATE TABLE IF NOT EXISTS article_chunk (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    chunk TEXT NOT NULL,
    chunk_id INTEGER NOT NULL, -- a sequential incremental id for the chunk to identify the location of the chunk in the article
    -- embedding is a 1D array of floats with a size of 512
    embedding vector(1536) NOT NULL, -- 1536 is the size of the embedding vector returned by the LLM
);

-- Return Type for the search function
CREATE TYPE article_chunk_search_result AS (
    article_id INTEGER,
    chunk TEXT,
    chunk_id INTEGER,
    created_at TIMESTAMP,
    search_rank REAL
);

-- Create a stored procedure that retrieves article chunks based based on full text search on the body_tsvector
CREATE OR REPLACE FUNCTION fts_search_article_chunks(search_term TEXT, num_chunks INTEGER, opt_month INTEGER DEFAULT NULL, opt_year INTEGER DEFAULT NULL)
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

CREATE OR REPLACE FUNCTION vector_search_article_chunks(embedding_vector vector, num_chunks INTEGER, opt_month INTEGER DEFAULT NULL, opt_year INTEGER DEFAULT NULL, similarity_threshold FLOAT DEFAULT 0.2)
RETURNS TABLE(article_id INTEGER, chunk TEXT, chunk_id INTEGER, article_title TEXT, created_at TIMESTAMP, score FLOAT) AS $$
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
    (1 - (ac.embedding <=> embedding_vector)) AS score, -- cosine distance
  FROM article_chunk ac
  WHERE  ac.embedding <=> embedding_vector < similarity_threshold AND -- Filter out chunks with cosine distance less than the similarty threshold
        (opt_month IS NULL OR EXTRACT(MONTH FROM ac.created_at) = opt_month) AND -- Filter by month if provided
        (opt_year IS NULL OR EXTRACT(YEAR FROM ac.created_at) = opt_year) -- Filter by year if provided
  ORDER BY score DESC
  LIMIT num_chunks;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION hybrid_vector_fulltext_search(
    search_term TEXT,
    embedding_vector VECTOR,
    num_chunks INTEGER = 10,
    rrf_k INTEGER = 60,
    full_text_weight float = 1, -- value between 0 and 1
    vector_weight float = 1,    -- value between 0 and 1
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
        fts_search_article_chunks(search_term, num_chunks * 2, opt_month, opt_year);

    -- Temporary table to store vector search results with RRF scores
    CREATE TEMP TABLE vector_search_results AS
    SELECT *,
           row_number() OVER (ORDER BY score DESC) AS rank
    FROM
        hybrid_search_article_chunks(embedding_vector, num_chunks * 2, opt_month, opt_year);

    -- Combining results from full text and vector search using RRF
    RETURN QUERY
    SELECT
        coalesce(ft.article_id, vs.article_id) AS article_id,
        coalesce(ft.chunk_id, vs.chunk_id) AS chunk_id,
        coalesce(ft.chunk, vs.chunk) AS chunk,
        coalesce(ft.created_at, vs.created_at) AS created_at,
        (coalesce(1.0/ (rrf_k + ft.rank),0.0) * full_text_weight + coalesce(1.0/ (rrf_k + vs.rank),0.0) * vector_weight )::double precision AS combined_score
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

-- updating the vector_search_summary function to include the date factor
CREATE OR REPLACE FUNCTION vector_search_summary(embedding_vector vector, num_chunks INTEGER, opt_month INTEGER DEFAULT NULL, opt_year INTEGER DEFAULT NULL, similarity_threshold FLOAT DEFAULT 0.2)
RETURNS TABLE(article_id INTEGER, chunk TEXT, article_title TEXT, created_at TIMESTAMP, score FLOAT) AS $$
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
    (
      0.8 * (1 - (a.summary_embedding <=> embedding_vector)) + -- Weighted cosine distance
      0.2 * (1 - (EXTRACT(EPOCH FROM current_date - a.created_at) / date_range)) -- Weighted normalized date factor, current_date is a psql internal function
    ) AS score,
  FROM article a
  WHERE  a.summary_embedding <=> embedding_vector < similarity_threshold AND -- Filter out chunks with cosine distance less than similarity_threshold
        (opt_month IS NULL OR EXTRACT(MONTH FROM a.created_at) = opt_month) AND -- Filter by month if provided
        (opt_year IS NULL OR EXTRACT(YEAR FROM a.created_at) = opt_year) -- Filter by year if provided
  ORDER BY score DESC
  LIMIT num_chunks;
END;
$$ LANGUAGE plpgsql;