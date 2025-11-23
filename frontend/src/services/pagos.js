import axios from '../axios'

export const createMercadoPagoPreference = (payload) => {
  return axios.post('pagos/mercadopago/preferencias/', payload)
}
