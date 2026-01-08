import api from '../axios';

export const getProductos = (params) => {
  return api.get('/productos/', { params });
};

export const getCategorias = () => {
  return api.get('/categorias/');
};

export const getMarcas = () => {
  return api.get('/marcas/');
};

export const getAtributos = () => {
  return api.get('/atributos-base/');
};

export const getValorAtributos = () => {
  return api.get('/atributos/');
};

export const getPriceRange = () => {
  return api.get('/price-range/');
};

export const getCategoriasTree = () => {
  return api.get('/all-categories/');
};
