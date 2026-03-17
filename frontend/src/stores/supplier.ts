// src/stores/supplier.ts (Pinia)
import { defineStore } from 'pinia'
import axios from '@/axios'
export const useSupplierStore = defineStore('supplier', {
  state: () => ({ cache: new Map<string, {in_stock:boolean, ts:number}>() }),
  actions: {
    async checkSku(sku: string) {
      const now = Date.now()
      const cached = this.cache.get(sku)
      if (cached && (now - cached.ts) < 5*60*1000) return cached
      const { data } = await axios.get(`suppliers/status`, { params: { sku } })
      const item = { in_stock: !!data.in_stock, ts: now }
      this.cache.set(sku, item)
      return item
    }
  }
})
