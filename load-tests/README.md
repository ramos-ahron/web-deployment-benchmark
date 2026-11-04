# load-tests

Owner: Ahron

k6 workload scripts for the WordPress site.

Planned contents:

- A k6 script with a configurable target URL, so it is not tied to one deployment.
- Browsing the home page and several posts, with 1 to 3 second think times and checks on status and page content.
- Instructions for running the test with different user counts.
- The 90% read / 10% write mix once write operations are confirmed to succeed. Until then, both deployments use the same read-only workload, labelled as preliminary.
- The run schedule and deployment order.

The k6 tutorial example only checks the installation. The experiment targets our own WordPress site.
