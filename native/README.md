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

## Native WordPress baseline

- [Installation and configuration](setup.md)
- [Dataset composition and regeneration](dataset.md)
- [Environment inventory](../infra/vm-inventory.md)

Run these commands from the repository root on the indicated VM:

| Command | VM | Purpose |
|---|---|---|
| `bash native/verify-web.sh` | seng533-web | Inspect the native baseline |
| `bash native/check-from-load.sh` | seng533-load | Check HTTP connectivity |
| `bash native/seed-posts.sh` | seng533-web | Populate a fresh one-post installation |

The existing site already contains 10,000 published posts. Do not regenerate it. The helper scripts were assembled after manual setup, syntax-checked, and have not been executed on RAC.
