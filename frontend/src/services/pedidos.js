import axios from '../axios';

export const getOrderByPreferenceId = (preferenceId) => {
  return axios.get(`/pedidos/by-preference/${preferenceId}/`);
};
