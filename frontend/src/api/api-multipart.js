// frontend/src/api/api-multipart.js
import api from '../axios'   // default import

export function postMultipart(url, formData) {
  return api.post(url, formData, {
    headers: {
      'Content-Type': null // Deja que Axios lo infiera y agregue el boundary
    }
  })
}
