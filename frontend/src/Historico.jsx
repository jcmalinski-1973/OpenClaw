import { useEffect, useState } from 'react'
import { listarPedidos, urlResultado } from './api'
import ProdutosPedido from './ProdutosPedido'

const STATUS_LABEL = {
  completed: { label: 'Concluído', cls: 'bg-green-100 text-green-700' },
  processing: { label: 'Processando', cls: 'bg-yellow-100 text-yellow-700' },
  failed: { label: 'Erro', cls: 'bg-red-100 text-red-700' },
}

function Badge({ status }) {
  const s = STATUS_LABEL[status] || { label: status, cls: 'bg-gray-100 text-gray-600' }
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${s.cls}`}>
      {s.label}
    </span>
  )
}

function formatDate(iso) {
  return new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
}

function PedidoRow({ pedido }) {
  const [expanded, setExpanded] = useState(false)

  return (
    <>
      <tr
        className="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
        onClick={() => setExpanded(e => !e)}
      >
        <td className="py-2 pr-2 text-gray-400 text-xs select-none w-4">
          {expanded ? '▾' : '▸'}
        </td>
        <td className="py-2 pr-4 text-gray-600 whitespace-nowrap">{formatDate(pedido.created_at)}</td>
        <td className="py-2 pr-4"><Badge status={pedido.status} /></td>
        <td className="py-2 pr-4 text-gray-700">{pedido.resumo?.order_items_found ?? '—'}</td>
        <td className="py-2 pr-4 text-gray-700">{pedido.resumo?.processed_ok ?? '—'}</td>
        <td className="py-2 pr-4 text-gray-700">{pedido.resumo?.items_with_additional ?? '—'}</td>
        <td className="py-2 pr-4 text-gray-500">{pedido.processing_time_seconds ? `${pedido.processing_time_seconds}s` : '—'}</td>
        <td className="py-2" onClick={e => e.stopPropagation()}>
          {pedido.status === 'completed' ? (
            <a
              href={urlResultado(pedido.id)}
              className="text-blue-600 hover:underline font-medium text-sm"
              download
            >
              Baixar
            </a>
          ) : pedido.status === 'failed' ? (
            <span className="text-red-500 text-xs" title={pedido.error_message}>Erro</span>
          ) : (
            <span className="text-gray-400 text-xs">—</span>
          )}
        </td>
      </tr>

      {expanded && (
        <tr className="border-b border-gray-100 bg-gray-50">
          <td colSpan={8} className="px-6 py-4">
            <ProdutosPedido pedidoId={pedido.id} />
          </td>
        </tr>
      )}
    </>
  )
}

export default function Historico({ refresh }) {
  const [data, setData] = useState(null)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  async function load(p = 1) {
    setLoading(true)
    setError(null)
    try {
      const res = await listarPedidos(p)
      setData(res)
      setPage(p)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(1) }, [refresh])

  if (error) return <p className="text-sm text-red-600">{error}</p>
  if (!data) return <p className="text-sm text-gray-400">Carregando...</p>

  return (
    <div>
      {data.items.length === 0 ? (
        <p className="text-sm text-gray-400 text-center py-8">Nenhum pedido processado ainda.</p>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-gray-200 text-left text-gray-500 text-xs uppercase tracking-wide">
              <th className="pb-2 w-4"></th>
              <th className="pb-2 pr-4">Data</th>
              <th className="pb-2 pr-4">Status</th>
              <th className="pb-2 pr-4">Itens</th>
              <th className="pb-2 pr-4">OK</th>
              <th className="pb-2 pr-4">Adicionais</th>
              <th className="pb-2 pr-4">Tempo</th>
              <th className="pb-2">Resultado</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map(p => (
              <PedidoRow key={p.id} pedido={p} />
            ))}
          </tbody>
        </table>
      )}

      {data.pages > 1 && (
        <div className="flex items-center gap-2 mt-4 text-sm">
          <button
            onClick={() => load(page - 1)}
            disabled={page <= 1 || loading}
            className="px-3 py-1 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50"
          >
            ← Anterior
          </button>
          <span className="text-gray-500">Página {page} de {data.pages}</span>
          <button
            onClick={() => load(page + 1)}
            disabled={page >= data.pages || loading}
            className="px-3 py-1 rounded border border-gray-300 disabled:opacity-40 hover:bg-gray-50"
          >
            Próxima →
          </button>
        </div>
      )}
    </div>
  )
}
