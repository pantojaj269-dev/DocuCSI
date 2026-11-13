import { afterEach, test } from 'node:test';
import assert from 'node:assert/strict';
import { apiRequest } from './api.js';

const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });

test('returns successful JSON', async () => {
  globalThis.fetch = async () => Response.json({ status: 'online' });
  assert.deepEqual(await apiRequest('/api/health'), { status: 'online' });
});

test('shows server error details without retrying a POST', async () => {
  let calls = 0;
  globalThis.fetch = async () => {
    calls += 1;
    return Response.json({ detail: 'Servidor ocupado' }, { status: 503 });
  };
  await assert.rejects(apiRequest('/api/analyze/full', { method: 'POST' }), /Servidor ocupado/);
  assert.equal(calls, 1);
});

test('handles structured validation errors', async () => {
  globalThis.fetch = async () => Response.json({ detail: [{ msg: 'Required' }] }, { status: 422 });
  await assert.rejects(apiRequest('/api/analyze/full'), /422/);
});

test('handles HTML returned by a misconfigured backend URL', async () => {
  globalThis.fetch = async () => new Response('<html>Loading</html>');
  await assert.rejects(apiRequest('/api/health'), /respuesta válida/);
});

test('explains a disconnected server', async () => {
  globalThis.fetch = async () => { throw new TypeError('Failed to fetch'); };
  await assert.rejects(apiRequest('/api/health'), /No se pudo conectar/);
});

function pendingFetch(_url, { signal }) {
  return new Promise((_resolve, reject) => {
    if (signal.aborted) reject(new DOMException('Aborted', 'AbortError'));
    else signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
  });
}

test('stops waiting when the timeout expires', async () => {
  globalThis.fetch = pendingFetch;
  await assert.rejects(apiRequest('/api/health', { timeoutMs: 5 }), /no respondió en 2 minutos/);
});

test('allows startup requests to be cancelled on unmount', async () => {
  globalThis.fetch = pendingFetch;
  const controller = new AbortController();
  const request = apiRequest('/api/health', { signal: controller.signal });
  controller.abort();
  await assert.rejects(request, { name: 'AbortError' });
});
