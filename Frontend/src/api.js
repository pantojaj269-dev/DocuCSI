export const API_BASE = (import.meta.env?.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '');

export async function apiRequest(path, { timeoutMs = 120000, signal, ...options } = {}) {
  const controller = new AbortController();
  const abort = () => controller.abort();
  signal?.addEventListener('abort', abort, { once: true });
  if (signal?.aborted) controller.abort();
  const timer = setTimeout(abort, timeoutMs);
  try {
    const response = await fetch(`${API_BASE}${path}`, { ...options, signal: controller.signal });
    let data;
    try {
      data = await response.json();
    } catch {
      if (controller.signal.aborted) throw new DOMException('Aborted', 'AbortError');
      throw new Error('El servidor no devolvió una respuesta válida. Verifica la URL del backend y vuelve a intentar.');
    }
    if (!response.ok) {
      throw new Error(typeof data.detail === 'string' ? data.detail : `Error del servidor (${response.status}). Vuelve a intentar.`);
    }
    return data;
  } catch (error) {
    if (error.name === 'AbortError' && !signal?.aborted) {
      throw new Error('El servidor no respondió en 2 minutos. Puede estar iniciándose en Render; espera unos segundos y vuelve a intentar.');
    }
    if (error instanceof TypeError) {
      throw new Error('No se pudo conectar con el servidor. Comprueba tu conexión y que el backend de Render esté disponible.');
    }
    throw error;
  } finally {
    clearTimeout(timer);
    signal?.removeEventListener('abort', abort);
  }
}
