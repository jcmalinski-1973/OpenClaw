import { useEffect, useState } from 'react'
import { listarProdutosPedido } from './api'

const STATUS_BADGE = {
  ok: 'bg-green-100 text-green-700',
  template_not_found: 'bg-yellow-100 text-yellow-800',
  stock_not_found: 'bg-orange-100 text-orange-700',
}

const STATUS_LABEL = {
  ok: 'OK',
  template_not_found: 'Sem template',
  stock_not_found: 'Sem estoque',
}

export default function ProdutosPedido({ pedidoId }) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    setLoading(true)
    setData(null)
    setError(null)
    listarProdutosPedido(pedidoId)
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [pedidoId])

  if (loading) return <p className="text-xs text-gray-400 py-3 text-center">Carregando produtos...</p>
  if (error) return <p className="text-xs text-red-500 py-3">{error}</p>
  if (!data || data.items.length === 0) return <p className="text-xs text-gray-400 py-3 text-center">Nenhum produto registrado.</p>

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr className="border-b border-gray-200 text-left text-gray-500 uppercase tracking-wide">
            <th className="pb-2 pr-3 whitespace-nowrap">Código</th>
            <th className="pb-2 pr-3">Descrição</th>
            <th className="pb-2 pr-3 text-right whitespace-nowrap">Emb.</th>
            <th className="pb-2 pr-3 text-right whitespace-nowrap">QP</th>
            <th className="pb-2 pr-3 text-right whitespace-nowrap">QA</th>
            <th className="pb-2 pr-3 text-right whitespace-nowrap">Total</th>
            <th className="pb-2 pr-3 text-right whitespace-nowrap">Recebido</th>
            <th className="pb-2 whitespace-nowrap">Status</th>
          </tr>
        </thead>
        <tbody>
          {data.items.map(p => (
            <tr key={p.id} className={`border-b border-gray-100 ${p.status !== 'ok' ? 'opacity-60' : ''}`}>
              <td className="py-1.5 pr-3 font-mono text-gray-700 whitespace-nowrap">{p.codigo}</td>
              <td className="py-1.5 pr-3 text-gray-700 max-w-[220px]">
                <span title={p.descricao} className="block truncate">{p.descricao}</span>
              </td>
              <td className="py-1.5 pr-3 text-right text-gray-500">{p.tamanho_embalagem || '—'}</td>
              <td className="py-1.5 pr-3 text-right text-gray-700">{p.qp}</td>
              <td className={`py-1.5 pr-3 text-right font-medium ${p.qa > 0 ? 'text-blue-600' : 'text-gray-400'}`}>
                {p.qa > 0 ? `+${p.qa}` : p.qa}
              </td>
              <td className="py-1.5 pr-3 text-right font-semibold text-gray-800">{p.total}</td>
              <td className="py-1.5 pr-3 text-right text-gray-500">{p.qtd_recebida ?? '—'}</td>
              <td className="py-1.5">
                <span className={`inline-block px-1.5 py-0.5 rounded text-xs font-medium ${STATUS_BADGE[p.status] || 'bg-gray-100 text-gray-600'}`}>
                  {STATUS_LABEL[p.status] || p.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="text-xs text-gray-400 mt-2">{data.total} produto{data.total !== 1 ? 's' : ''}</p>
    </div>
  )
}
