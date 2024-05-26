# Mastering Search and Retrieval in LLMs: Unveiling the Power of the RAG Pattern: Part 2

In this article, we continue our discussion of the RAG pattern and how it can be used to improve search and retrieval in LLMs. We will focus on implementing a simple RAG application in PostgreSQL. PostgreSQL has emerged as a unified platform for data from most domains. It has become a central piece when building most modern applications. Its open-source nature and the ability to extend its functionality via extensions make it a powerful tool for building modern applicators. We will discuss the PostgreSQL ecosystem and how when leveraging the core Postgresql data integrity guarantees along with some extensions, the effect becomes something like 1+1+1=6 in terms of the power, meaning that those feature stack up to deliver more than the sum of their parts.

In the previous article, we discussed full text search and the theory behind it. In this article we will be using out of the box full text search capabilities of PostgreSQL to implement a simple search engine. We will be using the `tsvector` and `tsquery` data types to implement full text search. We will also discuss how to use the `websearch_to_tsquery` function to convert a search query into a `tsquery` data type. We will also discuss how to use the `ts_rank` function to rank search results based on relevance.

We also discussed Vector Search and how it is one of the pillars of the RAG pattern and allows us to retrieve passages that are semantically similar to a given query. We will be using the relatively new `pgvector` extension to implement vector search in PostgreSQL. 

We will combine full text search and vector search to perform hybrid search which allows us to leverage the strengths of both approaches. As it has been shown that the combination of vector search and full text search can lead to better search results.
Finally we show how we can based on certain metrics boost certain search results over others, for example we can boost search results that are more recent or that are more popular based on external metrics criteria.

## PostgreSQL Ecosystem

## Table Schema
during this article, we will start building and enhancing the schema for our small search application. First we assume that we have a set of articles, with an Author, a Title and a publication date, and a body which is the actual content of the article.

```sql
CREATE TABLE IF NOT EXISTS article (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    body TEXT NOT NULL,
    author TEXT , -- can be null if the author(s) is not known
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    -- updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```
This table schema does not lend itself to a proper search application just yet, the problem is the operations we can do is perhaps filter on certain date ranges. Or perhaps of we know the exact title of an article or an exact author name. Or perhaps we can search for a specific word in the body of the article. But we cannot do more advanced search operations such as searching for articles that contain a certain word in the title and another word in the body. Or searching for articles that contain a certain word in the title and another word in the body and were published after a certain date. queries like `Like` or `ILike` can be used to search for a word in the title or the body of the article. The problem with those queries is that thee require a full table scan to be performed, which can be very slow for large tables. We need a way to perform a quick search and look up an index in the table to find the relevant articles.

```sql
-- example of query using Like or ILike to search for a word in the title or the body of the article
SELECT * FROM article WHERE title ILIKE '%fish%' OR body ILIKE '%ocean%';
```
## Full Text Search in PostgreSQL

Full text search to the rescue! As discussed earlier Full text search performs a reverse document lookup and segments words into lexigrams as explained in Part 1 of the Article. The first step is to create a `tsvector` column in the table that will store the lexigrams of the article title and body. So far we have only created that list of lexigrams in the `tsvector` column, but we have not yet created an index on that column. 
We can then create a `GIN` index on the `tsvector` column to speed up full text search queries. The GIN is a Generalized Inverted Index which is exactly what we are looking for. One last step that we have to add is to actually populate the `tsvector` column with the lexigrams of the article title and body. We can do this by using the `to_tsvector` function to convert the article title and body into a `tsvector` data type and store it in the `tsvector` column. 

```sql
-- add a tsvector column to store the lexigrams of the article title and body
ALTER TABLE article ADD COLUMN body_tsvector tsvector;
ALTER TABLE article ADD COLUMN title_tsvector tsvector;
-- create a GIN index on the tsvector column
CREATE INDEX article_body_tsvector_idx ON article USING GIN(body_tsvector);
CREATE INDEX article_title_tsvector_idx ON article USING GIN(title_tsvector);
-- populate the tsvector column with the lexigrams of the article title and body
UPDATE article SET body_tsvector = to_tsvector('english', body);
UPDATE article SET title_tsvector = to_tsvector('english',title);
```
Now we can perform full text search queries using the `@@` operator to search for articles that contain certain words in the title or body. The `@@` operator returns true if the `tsvector` column contains the lexigrams of the search query. We can also use the `websearch_to_tsquery` function to convert a search query into a `tsquery` data type. The `websearch_to_tsquery` function is useful for converting a search query into a `tsquery` data type that can be used in full text search queries. 

```sql
-- search for articles that contain the word 'fish' in the title or body
SELECT a.title, a.link FROM article a WHERE a.title_tsvector @@ to_tsquery('english', 'fish') OR a.body_tsvector @@ to_tsquery('english', 'fish');
-- If we want to use a sentence as a search query we can use the websearch_to_tsquery function
SELECT a.title, a.link FROM article a WHERE a.body_tsvector @@ websearch_to_tsquery('english', 'fish in the ocean');
```

### Using triggers to update the tsvector column

One important point we have to mention is that we have to update the `tsvector` column every time the article title or body is updated. We can use triggers to automatically update the `tsvector` column when the article title or body is updated. We can create a trigger function that updates the `tsvector` column when the article title or body is updated. We can then create a trigger that calls the trigger function when the article title or body is updated. 

```sql
-- create a trigger function that updates the tsvector column when the article title or body is updated
CREATE OR REPLACE FUNCTION article_trigger() RETURNS trigger AS $$
begin
  new.title_tsvector := to_tsvector('english', new.title);
  new.body_tsvector := to_tsvector('english', new.body);
  return new;
end
$$ LANGUAGE plpgsql;

CREATE TRIGGER article_update BEFORE INSERT OR UPDATE
ON article FOR EACH ROW EXECUTE FUNCTION article_trigger();
```

## PgVector: Vector Search in PostgreSQL

Vector search is one of the pillars of the RAG pattern and allows us to retrieve passages that are semantically similar to a given query. We will be using the relatively new `pgvector` extension to implement vector search in PostgreSQL. The `pgvector` extension provides a set of functions and operators to perform vector operations in PostgreSQL. We can use the `pgvector` extension to store vectors in a table and perform vector operations on those vectors. we should note that `pgvector` works with any vectors and is not seomthing special for Large Language Models. It allows you to compare the distance between vectors and perform other vector operations. for example

```sql
-- Calculate the cosine similarity between two vectors [0,1] [1,0], <=> is the cosine similarity operator
SELECT '[0,1]'::vector(2) <=> '[1,0]'::vector(2); -- 1 , because these two vectors are orthogonal
-- Calculate the L2 distance between two vectors [0,1] [1,0], <+> is the L2 distance operator
SELECT '[0,1]'::vector(2) <+> '[1,0]'::vector(2); -- 1.4142~ which is sqrt(2) , because these two vectors are orthogonal
```
As we can see this is library can be used for any vector operations and is not exclusive to embeddings or LLMs.

When we want to perform semantic search, as explained in Part 1 of the article we get the embedding of the query and compare it against chunks of the document embeddings to get the closest article pieces. We need to break up the original document into chunks and store the embeddings of those chunks in a table. We can then compare the embedding of the query against the embeddings of the chunks to get the closest chunks to the query. This is done because LLMs embedding have a maxiumu size and typically most articles or documents do not fit in that window and we have to operate on smaller chunks.

The SQL snippet below describes the article_chunk table  
```sql
CREATE TABLE IF NOT EXISTS article_chunk (
    id SERIAL PRIMARY KEY,
    article_id INTEGER NOT NULL,
    chunk TEXT NOT NULL,
    chunk_id INTEGER NOT NULL, -- a sequential incremental id for the chunk to identify the location of the chunk in the article
    -- embedding is a 1D array of floats with a size of 512
    embedding vector(1536) NOT NULL, -- 1536 is the size of the embedding vector returned by the LLM
);
```
1. Note that we need to call am embedding model such as `ada-text-embedding-2` or `ada-text-embedding-3-small` to obtain the embeddings of the chunk. The `1536` is the embedding vector size returned by that particular model.
2. We need to write a script that for reach article in the `article` database, we break up the article into smaller chunks and for each chunk we get the embedding and store it in the `article_chunk` table. This can be done very easily in Python. I in a subseqnt post, I will share a SQL stored procedure that does this operation.
3. We see that we if we want to perform both vector search and full text search, then we need to query 2 tables: the `article` table for the full text search and the `article_chunk` table for the vector search. We can simplify this be also storing the `tsvector` of the chunk in the `article_chunk` table and create a GIN index on that column. This way we can perform full text search and vector search on the `article_chunk` table. Similarly we can create a trigger function that updates the `tsvector` column when the chunk is updated, and we can demoralize the `article_chunk` by also storing the `author` and `created_at`, `link` and `title` columns in the `article_chunk` table. This may increase storage size a bit, but it makes the search queries much faster as we only have to query one table instead of two where we would have to perform expensive joins.

## Hybrid Search in PostgreSQL

### Full Text Search Query

So how we do we perform full text search? Below is a SQL Function that performs that

```sql
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
```

This query basically takes a search term and returns the chunks that contain that search term. We can also filter the results based on the month and year of the article. We can use the `ts_rank` function to rank the search results based on relevance. The `ts_rank` function returns a rank value that indicates how relevant the search term is to the chunk. We can then order the search results by the rank value and return the top `num_chunks` that match the query. Note that similar to the month and year, we cam also add optional parameters to filter the search results based on the author or the title of the article.

### Vector Search Query

Below is a SQL Function that performs that

```sql
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
```

So let us dig a little into what the `vector_search_article_chunks` function does. It takes an embedding vector as input and returns the chunks that are semantically similar to the embedding vector. We can also filter the results based on the month and year of the article if provided. We perform this by using the `<=>` operator to calculate the cosine similarity between the embedding vector and the embedding of the chunk. We can then order the search results by the cosine similarity and return the top `num_chunks` that are similar to the embedding vector. We can also add an optional parameter to filter the search results based on a `similarity_threshold`. This allows us to filter out chunks that are not similar enough to the embedding vector, this similarity threshold is application use specific and should be tuned based on the application requirements and experimentation. 

Note that we did not put any filter on the full text search query because the operation `ac.chunk_tsvector @@ query` would only return chunks that contain the search term, so we do not need to filter the results based on the similarity threshold And even lower ranked chunks are guaranteed to at least be partially relevant to the search term even so slightly. This is NOT the case for the vector search query, where any two vectors, their distance is always between 0 and 1 and that operation `(1 - (ac.embedding <=> embedding_vector)) AS score` would need a threshold to filter out the chunks that are not similar enough to the query based on the application use case.

### Hybrid Search Query

So far great we have two functions that perform full text search and vector search. But how do we combine them? Below is a SQL Function that performs that. The key idea is to use an algorithm that `merges` the fts and vector search results based on a certain criteria. In this case we use the `score` from the vector search and the `search_rank` from the full text search to merge the results. A simple approach would be to merge the results in a round robin fasigon, get one from fts results, one from vector, one from fts and so on. But we can also use a more sophisticated approach such as the relative strength (or rank) of each search method to perform reranking of the results. We will be using the (Reciprocal Rank Fusion)[https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking] algorithm (RFF) to merge the results. 

```sql
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
```

Ok, let us dig in a little and breakdown what is happening in the `hybrid_vector_fulltext_search` function. The function takes a search term and an embedding vector as input. It calls both the `fts_search_article_chunks` and `vector_search_article_chunks` functions to perform full text search and vector search respectively. The function then combines the results from the full text search and the vector search using the RRF algorithm. The RRF algorithm assigns a score to each search result based on the rank of the search result. The RRF algorithm assigns a higher score to search results that have a higher rank. The function then returns the top `num_chunks` that match the query based on the combined score. The function also allows us to specify the `full_text_weight` and `vector_weight` parameters which are the weights assigned to the full text search and the vector search results respectively. 

## Scoring Profiles and Custom metrics

One last modifiction we can make is that typiclly in article search applications, we want to boost more recent documents over older documents even if they are a little bit less relevant, how can this typically be acheived? We can modify both the `fts_search_article_chunks` and `vector_search_article_chunks` functions to include a `freshness` that boosts the score of more recent articles. We can then use the `freshness` to boost the score of more recent articles. We can also add other custom metrics such as the popularity of the article or the author of the article to boost the score of certain search results over others. 

```sql
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
```

## Summary and Future Work

So In this article we have discussed how to implement a simple search engine in PostgreSQL using the RAG pattern. We have discussed how to perform full text search and vector search in PostgreSQL. We have also discussed how to combine full text search and vector search to perform hybrid search. We have also discussed how to use the RRF algorithm to merge the results from full text search and vector search. We have also discussed how to add custom metrics such as the freshness of the article or the popularity of the article to boost the score of certain search results over others. While there are many options for platforms to build on search applications, such as Azure AI Search, Elasticsearch or a myriad of the new vector databases released fro this purpose. Postgresql remains a solid choice for building search applications due to the fact that it still offers strong data integrity guarantees and offers true Transactions. Moreover, you get all the benefits of the Postgresql ecosystem such as backup and restore, Change Data Capture and streaming to practically any other data store. Moreover, you can perform near real time on data at very high scale if you stream the data to a data warehouse such as Azure Synapse, Google Query or Amazon Redshift, Clickhouse and even most recently DuckDb.

In the next article, I will discuss how to scale this solution beyond a single Postgresql instance voa the Azure Cosmos Db for Postgresql (Previously Citus Db). This allows to partition our documents and achieve higher write throughput in cases where it is needed. Also I am working on a small Postgresql extension that automates many of the steps explained in this article, so stay tuned for that! 


