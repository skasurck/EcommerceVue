/**
 * Convierte un nombre de producto de MAYÚSCULAS a Title Case inteligente.
 *
 * Reglas:
 * - Palabras con números se mantienen en MAYÚSCULAS (T2U, AC600, 150MBPS, 5GHz)
 * - Preposiciones y artículos cortos en minúsculas (de, del, con, para, y, o, a, en)
 * - Todo lo demás: primera letra en mayúscula
 *
 * Ejemplo:
 *   "ADAPTADOR TPLINK ARCHER T2U AC600 DUAL BAND 150MBPS 5GHZ 12M DE GARANTIA"
 *   → "Adaptador Tplink Archer T2U AC600 Dual Band 150MBPS 5GHz 12M de Garantia"
 */

const LOWERCASE_WORDS = new Set([
  'de', 'del', 'la', 'las', 'los', 'el', 'un', 'una', 'unos', 'unas',
  'con', 'para', 'por', 'sin', 'sobre', 'entre', 'y', 'o', 'a', 'en',
])

export function toProductTitle(str) {
  if (!str) return ''
  const words = str.trim().toLowerCase().split(/\s+/)
  return words
    .map((word, index) => {
      if (!word) return ''
      // Palabras con números: MAYÚSCULAS completas (T2U, AC600, 150MBPS, 12M)
      if (/\d/.test(word)) return word.toUpperCase()
      // Preposiciones/artículos en minúsculas (excepto la primera palabra)
      if (index > 0 && LOWERCASE_WORDS.has(word)) return word
      // Todo lo demás: capitalizar primera letra
      return word.charAt(0).toUpperCase() + word.slice(1)
    })
    .join(' ')
}
