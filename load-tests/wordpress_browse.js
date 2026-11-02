import http from 'k6/http';
import { sleep } from 'k6';

const BASE = __ENV.BASE_URL;
const VUS = Number(__ENV.VUS || 1);
const WARMUP = __ENV.WARMUP || '2m';
const DURATION = __ENV.DURATION || '5m';
const IDS = (__ENV.POST_IDS || '').split(',').filter(Boolean);

if (!BASE || IDS.length === 0) throw new Error('set BASE_URL and POST_IDS');

const scenario = (phase, startTime) => ({
  executor: 'constant-vus', vus: VUS, duration: phase === 'warmup' ? WARMUP : DURATION,
  startTime, tags: { phase },
});

export const options = {
  scenarios: { warmup: scenario('warmup', '0s'), measure: scenario('measure', WARMUP) },
  thresholds: {
    'http_req_failed{phase:measure}': ['rate<0.01'],
    'http_req_duration{phase:measure}': ['p(95)>=0'],
    'http_reqs{phase:measure}': ['count>=0'],
  },
};

const think = () => sleep(1 + Math.random() * 2);

export default function () {
  const pick = () => IDS[Math.floor(Math.random() * IDS.length)];
  http.get(`${BASE}/`); think();
  for (let i = 0; i < 3; i++) { http.get(`${BASE}/?p=${pick()}`); think(); }
}
