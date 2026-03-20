const BASE = import.meta.env.VITE_API_URL || ''

export async function criarPedido(pedidoPdf, relatorioPdf, templateXlsx) {
  const form = new FormData()
  form.append('pedido_pdf', pedidoPdf)
  form.append('relatorio_pdf', relatorioPdf)
  form.append('template_xlsx', templateXlsx)

  const res = await fetch(`${BASE}/pedidos`, { method: 'POST', body: form })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `Erro ${res.status}`)
  }
  return res.json()
}

export async function listarPedidos(page = 1, limit = 20, status = '') {
  const params = new URLSearchParams({ page, limit })
  if (status) params.append('status', status)

  const res = await fetch(`${BASE}/pedidos?${params}`)
  if (!res.ok) throw new Error(`Erro ${res.status}`)
  return res.json()
}

export async function obterPedido(id) {
  const res = await fetch(`${BASE}/pedidos/${id}`)
  if (!res.ok) throw new Error(`Erro ${res.status}`)
  return res.json()
}

export function urlResultado(id) {
  return `${BASE}/pedidos/${id}/resultado`
}
