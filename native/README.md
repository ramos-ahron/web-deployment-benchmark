# native

Owner: Nathan

Native WordPress on the web VM, plus the test dataset.

Planned contents:

- Installation steps for the web server, PHP, and WordPress, using the versions listed in `infra/vm-inventory.md`.
- A `wp-config.example.php` with placeholder values. The real `wp-config.php` is ignored by Git.
- How the test dataset was created, and the actual post and comment counts. The proposal targets 10,000 posts and 50,000 comments.
- How to restore the baseline database backup and WordPress files.
- How to start and stop the native deployment.
- A list of testable pages for the load tests.

The baseline backup stays on the VMs. Record its path here.
