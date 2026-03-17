import api from '@/axios';

export const obtenerDirecciones = () => api.get('direcciones/');
export const obtenerMetodosEnvio = () => api.get('metodos-envio/');
export const crearPedido = (data) => api.post('pedidos/', data);
