import http from 'k6/http';
import { sleep } from 'k6';

const BASE = __ENV.BASE_URL;
const VUS = Number(__ENV.VUS || 1);
const DURATION = __ENV.DURATION || '5m';
const IDS = (__ENV.POST_IDS || '').split(',').filter(Boolean);

if (!BASE || IDS.length === 0) throw new Error('set BASE_URL and POST_IDS');

export const options = { vus: VUS, duration: DURATION };

const think = () => sleep(1 + Math.random() * 2);

export default function () {
  const pick = () => IDS[Math.floor(Math.random() * IDS.length)];
  http.get(`${BASE}/`); think();
  for (let i = 0; i < 3; i++) { http.get(`${BASE}/?p=${pick()}`); think(); }
}
