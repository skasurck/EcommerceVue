// frontend/src/api/api-multipart.js
import api from '../axios'   // default import

export function postMultipart(url, formData) {
  // Quita el header JSON global para que axios agregue el boundary de multipart
  const headers = { ...(api.defaults.headers.common || {}) }
  delete headers['Content-Type']
  return api.post(url, formData, { headers })
}
