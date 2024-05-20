# Commands

## 

```bash
export PGPASSWORD=postgres
 psql -h postgres -U postgres  -p 5432 -d newsanalysis
```

## Notes:
1. Performing full text search with websearch_to_tsquery does not work as exptecd for question asking since the results are sparse
Need to perform vector search on the summary


## Obserations
Original scan without index

('Function Scan on get_similar_chunks  (cost=0.25..10.25 rows=1000 width=96) (actual time=1247.604..1247.606 rows=10 loops=1)',)
('Planning Time: 0.119 ms',)
('Execution Time: 1248.221 ms',)

