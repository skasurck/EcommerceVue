import axios from '@/axios';

export const getOrderByPreferenceId = (preferenceId) => {
  return axios.get(`/pedidos/by-preference/${preferenceId}/`);
};

export const getPublicOrderById = (pedidoId) => {
  return axios.get(`/pedidos/public/${pedidoId}/`);
};

export const cancelarPedidoMP = (pedidoId) => {
  return axios.post(`pedidos/${pedidoId}/cancelar-mp/`);
};
