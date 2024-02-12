-- Postgresql

SELECT a.president, COUNt(a.id) as count
FROM article a
GROUP BY a.president;

COPY(
WITH WordCounts AS (
  SELECT
    id,
    LENGTH(regexp_replace(body, '\S+', 'x', 'g')) AS word_count
  FROM
    article
)

SELECT
  FLOOR(word_count / 100.0) * 100 AS word_bucket,
  COUNT(*) AS records
FROM WordCounts
GROUP BY word_bucket
ORDER BY word_bucket) TO '/tmp/results.csv' WITH CSV HEADER;

