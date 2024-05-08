# Commands

## 

```bash
export PGPASSWORD=postgres
 psql -h postgres -U postgres  -p 5432 -d newsanalysis
```

## Notes:
1. Performing full text search with websearch_to_tsquery does not work as exptecd for question asking since the results are sparse
Need to perform vector search on the summary