import { defineStore } from 'pinia';

export const useCheckoutStore = defineStore('checkout', {
  state: () => ({
    step: 1,
    direccion: {
      nombre: '',
      apellidos: '',
      email: '',
      nombre_empresa: '',
      calle: '',
      numero_exterior: '',
      numero_interior: '',
      colonia: '',
      ciudad: '',
      pais: '',
      estado: '',
      codigo_postal: '',
      telefono: '',
      referencias: '',
      save: false,
    },
    metodoEnvio: null,
    indicaciones: '',
    metodoPago: '',
    cupon: null,      // { id, codigo, descripcion, tipo, valor, descuento }
    descuento: 0,
  }),
  actions: {
    aplicarCupon(cuponData) {
      this.cupon = cuponData;
      this.descuento = Number(cuponData.descuento);
    },
    quitarCupon() {
      this.cupon = null;
      this.descuento = 0;
    },
    reset() {
      this.step = 1;
      this.direccion = {
        nombre: '',
        apellidos: '',
        email: '',
        nombre_empresa: '',
        calle: '',
        numero_exterior: '',
        numero_interior: '',
        colonia: '',
        ciudad: '',
        pais: '',
        estado: '',
        codigo_postal: '',
        telefono: '',
        referencias: '',
        save: false,
      };
      this.metodoEnvio = null;
      this.indicaciones = '';
      this.metodoPago = '';
      this.cupon = null;
      this.descuento = 0;
    },
  },
});
