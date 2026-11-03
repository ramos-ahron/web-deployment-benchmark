import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const BASE = __ENV.BASE_URL;
const VUS = Number(__ENV.VUS || 1);
const WARMUP = __ENV.WARMUP || '2m';
const DURATION = __ENV.DURATION || '5m';
const IDS = (__ENV.POST_IDS || '').split(',').filter(Boolean);
const MARKER = __ENV.MARKER || 'wp-content';
const WRITES = __ENV.WRITES === '1';
const WORKLOAD = WRITES ? 'read-write-90-10' : 'read-only-preliminary';

if (!BASE || IDS.length === 0) throw new Error('set BASE_URL and POST_IDS');

const appFail = new Rate('app_check_failed');
const verify = (r, checks) => appFail.add(r.status > 0 && r.status < 400 && !check(r, checks));

const scenario = (phase, startTime) => ({
  executor: 'constant-vus', vus: VUS, duration: phase === 'warmup' ? WARMUP : DURATION,
  startTime, tags: { phase },
});

export const options = {
  tags: { workload: WORKLOAD },
  scenarios: { warmup: scenario('warmup', '0s'), measure: scenario('measure', WARMUP) },
  thresholds: {
    'http_req_failed{phase:measure}': ['rate<0.01'],
    'app_check_failed{phase:measure}': ['rate<0.01'],
    'http_req_duration{phase:measure}': ['p(95)>=0'],
    'http_reqs{phase:measure}': ['count>=0'],
  },
};

const think = () => sleep(1 + Math.random() * 2);

function read(path, name) {
  const r = http.get(`${BASE}${path}`, { tags: { name } });
  verify(r, { 'status 200': (x) => x.status === 200, 'has marker': (x) => (x.body || '').includes(MARKER) });
  think();
}

function comment(id) {
  const body = { comment_post_ID: id, comment_parent: '0', author: 'k6', email: 'k6@example.com',
                 comment: `k6 ${__VU}-${__ITER}-${Date.now()}`, submit: 'Post Comment' };
  const r = http.post(`${BASE}/wp-comments-post.php`, body, { redirects: 0, tags: { name: 'comment' } });
  // WordPress answers a saved comment with a 302 to .../#comment-<id>
  verify(r, { 'comment saved': (x) => x.status === 302 && (x.headers['Location'] || '').includes('#comment-') });
  think();
}

export default function () {
  const pick = () => IDS[Math.floor(Math.random() * IDS.length)];
  if (WRITES && Math.random() < 0.1) return comment(pick());
  read('/', 'home');
  for (let i = 0; i < 3; i++) read(`/?p=${pick()}`, 'post');
}
