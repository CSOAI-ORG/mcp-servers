#!/usr/bin/env python3
"""
MEOK AI Labs - Load Testing
k6 load test script for API
"""

import http from "k6/http";
import { check, sleep } from "k6";
import { Rate, Trend } from "k6/metrics";

const BASE_URL = __ENV.API_URL || "http://localhost:8000";

const errorRate = new Rate("errors");
const latency = new Trend("latency");

const endpoints = [
  { method: "GET", path: "/health" },
  { method: "POST", path: "/governance/analyze" },
  { method: "POST", path: "/memory" },
  { method: "GET", path: "/memory?q=test" },
  { method: "GET", path: "/consciousness/state" },
];

const headers = {
  "Content-Type": "application/json",
  "X-API-Key": __ENV.API_KEY || "test-key-12345678901234567890123456789012",
};

export const options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "1m", target: 50 },
    { duration: "2m", target: 100 },
    { duration: "1m", target: 50 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<500", "p(99)<1000"],
    errors: ["rate<0.05"],
  },
};

export default function () {
  const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
  
  const start = Date.now();
  
  let res;
  let success = false;

  if (endpoint.method === "GET") {
    res = http.get(`${BASE_URL}${endpoint.path}`, { headers });
    success = res.status === 200;
  } else {
    const body = endpoint.path.includes("governance")
      ? JSON.stringify({
          content: "This is a test content for load testing",
          framework: "constitutional",
        })
      : JSON.stringify({
          content: "Test memory content",
          type: "semantic",
          tags: ["test"],
          importance: 0.5,
        });

    res = http.post(`${BASE_URL}${endpoint.path}`, body, { headers });
    success = res.status === 200 || res.status === 201;
  }

  latency.add(Date.now() - start);
  errorRate.add(!success);

  check(res, {
    "status is 200": (r) => r.status === 200 || r.status === 201,
    "has body": (r) => r.body && r.body.length > 0,
    "response time < 500ms": (r) => r.timings.duration < 500,
  });

  sleep(Math.random() * 2 + 0.5);
}

export function handleSummary(data) {
  return {
    stdout: textSummary(data, { indent: " ", enableColors: true }),
    "summary.json": JSON.stringify(data),
  };
}

function textSummary(data, options) {
  const indent = options.indent || "";
  const enableColors = options.enableColors || false;

  let output = "\n" + indent + "=== MEOK AI Load Test Results ===\n\n";

  output += indent + "HTTP Metrics:\n";
  output += indent + `  Requests: ${data.metrics.http_reqs?.values?.count || 0}\n`;
  output += indent + `  Failed: ${(data.metrics.http_req_failed?.values?.rate || 0) * 100}%\n`;
  output += indent + `  Avg Duration: ${data.metrics.http_req_duration?.values?.avg?.toFixed(2)}ms\n`;
  output += indent + `  P95 Duration: ${data.metrics.http_req_duration?.values?.["p(95)"]?.toFixed(2)}ms\n`;
  output += indent + `  P99 Duration: ${data.metrics.http_req_duration?.values?.["p(99)"]?.toFixed(2)}ms\n`;

  output += "\n" + indent + "Custom Metrics:\n";
  output += indent + `  Error Rate: ${(data.metrics.errors?.values?.rate || 0) * 100}%\n`;
  output += indent + `  Latency Avg: ${data.metrics.latency?.values?.avg?.toFixed(2)}ms\n`;

  return output;
}
