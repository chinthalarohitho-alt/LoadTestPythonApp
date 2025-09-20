import http from 'k6/http';
import { check, sleep } from 'k6';

function getByPath(obj, path) {
  try {
    return path.split('.').reduce((o, k) => (o && (k in o)) ? o[k] : undefined, obj);
  } catch (e) {
    return undefined;
  }
}

function tpl(str, row) {
  if (str === undefined || str === null) return '';
  return String(str).replace(/\{\{(\w+)\}\}/g, function(_, k) {
    return row && row[k] !== undefined ? String(row[k]) : '';
  });
}

export let options = {"stages": [{"duration": "10s", "target": 100}, {"duration": "50s", "target": 100}], "thresholds": {"http_req_duration": ["p(95)<800"], "checks": ["rate>0.98"]}, "tags": {"env": "demo", "service": "httpbin"}};

export default function () {

  const row = null;

}
