================================================================================
# 08 Performance Testing
================================================================================

# Performance Testing

## Purpose

Performance tests ensure the system meets its latency, throughput, and resource usage targets under expected load conditions. They detect regressions before they reach users.

---

## Test Scenarios

| Scenario | Metric | Target | Tools |
|---|---|---|---|
| Evidence query | p95 latency | < 100ms (1000 items) | k6, custom script |
| Insight retrieval | p95 latency | < 200ms (full chain) | k6, custom script |
| Reasoning pipeline | End-to-end latency | < 5s (complex) | Custom script |
| Graph traversal | p95 latency | < 500ms (1000 nodes) | Custom script |
| Concurrent API requests | Throughput | > 100 req/s | k6 |
| Frontend rendering | Time to interactive | < 3s | Lighthouse |

## Regression Thresholds

| Metric | Warning | Blocking |
|---|---|---|
| API p95 latency | > 1.5x baseline | > 3x baseline |
| Reasoning pipeline | > 2x baseline | > 4x baseline |
| Frontend TTI | > 4s | > 6s |
| Memory usage | > 1.5x baseline | > 2x baseline |

## Example

```bash
# k6 script for API performance test
import http from 'k6/http'
import { check, sleep } from 'k6'

export const options = {
    stages: [
        { duration: '30s', target: 10 },  // Ramp up
        { duration: '1m', target: 50 },   // Steady
        { duration: '30s', target: 0 },   // Ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<200'],
    },
}

export default function () {
    const res = http.get('http://localhost:8000/v1/insights?per_page=50')
    check(res, { 'status is 200': (r) => r.status === 200 })
    sleep(1)
}
```
