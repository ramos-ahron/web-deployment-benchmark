# Test dataset

Current verified state: 10,000 published posts, consisting of the original Hello world post plus 9,999 generated posts. Each generated post has the same 20 HTML paragraphs from `native/seed/test-post-content.html`. Generation took approximately 11 minutes on this setup. Dates and IDs are assigned by WordPress; recreating posts is not a byte-identical restoration.

The original SQL inspection showed one published page, one draft page, one auto-draft post, one published navigation entry, and one comment. Those counts have not been rechecked after seeding. No command in this package generates comments. The proposed 50,000-comment workload remains pending. Do not claim that target has been reached.

The current dataset is synthetic, text-only, and repetitive. It does not represent varied media sizes, realistic search selectivity, or a production content distribution. Keep it the same across deployments and state this limitation in the report.

## Existing site

Do not seed again: the 10,000-post target is already reached. Use the shared database or a controlled restore of its private snapshot to preserve the same IDs/content. Agree on a period without edits during benchmarks. If tests write comments or posts, restore/reset the dataset between runs using a separately reviewed recovery procedure.

## Fresh-site recreation

Copy/clone the repo to the web VM, then run from its root:

```bash
bash native/seed-posts.sh
```

The script requires the current count to be exactly one, that post to be ID 1 titled Hello world!, and WordPress to be 6.9.11. It refuses a partial or populated dataset. At 10,000 it exits without adding anything; this count check is not a content-integrity check. It uses the same content-generation mechanism as the completed run. Script syntax was checked locally; it has not been run on RAC. If interrupted, inspect the count and resolve the partial run before continuing. Do not blindly rerun the original unguarded generator.

## URL handoff

Ahron should query actual published URLs/IDs, not assume IDs are contiguous. On web, this read-only command exports URLs:

```bash
sudo -u www-data wp --path=/var/www/html post list --post_type=post --post_status=publish --field=url > ~/seng533-setup/post-urls.txt
```

Validate sampled URLs from the load VM before benchmarking. Agree on home/post/search traffic mix, think time, and whether only HTML or also assets are requested; keep those identical across modes.
