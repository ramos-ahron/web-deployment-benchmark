# analysis

Owner: Aaron

Scripts that read files from `results/` and produce:

- p95 response time against concurrent users.
- Successful requests per second against concurrent users.
- Web host CPU utilization against concurrent users.
- A table of error rate and memory usage.

Figures show variation between repetitions and separate HTTP failures from failed application checks. Output figures go to `report/figures/`.
