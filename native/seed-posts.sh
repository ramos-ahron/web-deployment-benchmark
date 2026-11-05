#!/usr/bin/env bash
# New guarded wrapper for the completed manual procedure. Do not run during tests.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
content="$script_dir/seed/test-post-content.html"
wp_cmd=(sudo -u www-data wp --path=/var/www/html)
version=$("${wp_cmd[@]}" core version)
[[ "$version" == 6.9.11 ]] || { printf 'Expected WordPress 6.9.11; found %s.\n' "$version" >&2; exit 1; }
count=$("${wp_cmd[@]}" post list --post_type=post --post_status=publish --format=count)
if [[ "$count" == 10000 ]]; then
  printf 'Already 10,000 published posts. No posts added. Count does not verify content.\n'
  exit 0
fi
[[ "$count" == 1 ]] || { printf 'Expected a fresh one-post site; found %s. Refusing to add posts.\n' "$count" >&2; exit 1; }
ids=$("${wp_cmd[@]}" post list --post_type=post --post_status=publish --format=ids)
[[ "$ids" == 1 ]] || { printf 'Expected published post ID 1.\n' >&2; exit 1; }
title=$("${wp_cmd[@]}" post get 1 --field=post_title)
[[ "$title" == 'Hello world!' ]] || { printf 'Unexpected initial post title.\n' >&2; exit 1; }
[[ -s "$content" ]] || { printf 'Missing content template.\n' >&2; exit 1; }
"${wp_cmd[@]}" post generate --count=9999 --post_type=post --post_status=publish --post_author=seng533admin --post_content < "$content"
count=$("${wp_cmd[@]}" post list --post_type=post --post_status=publish --format=count)
printf 'Published posts: %s\n' "$count"
[[ "$count" == 10000 ]]
