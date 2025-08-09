export function money(val){
  return new Intl.NumberFormat('es-MX',{style:'currency',currency:'MXN'}).format(val)
}

export function formatFecha(value){
  const d = new Date(value)
  const pad = n => n.toString().padStart(2,'0')
  return `${pad(d.getDate())}/${pad(d.getMonth()+1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}
