import { useState } from 'react'
import UploadForm from './UploadForm'
import Historico from './Historico'

const TABS = ['Novo Pedido', 'Histórico']

function SucessoBanner({ pedido, onNovo }) {
  return (
    <div className="rounded-lg bg-green-50 border border-green-200 p-5 space-y-3">
      <div className="flex items-center gap-2">
        <span className="text-green-600 text-xl">✓</span>
        <h3 className="font-semibold text-green-800">Pedido processado com sucesso</h3>
      </div>
      {pedido.resumo && (
        <dl className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm text-gray-700">
          <div><dt className="text-gray-500">Itens encontrados</dt><dd className="font-medium">{pedido.resumo.order_items_found}</dd></div>
          <div><dt className="text-gray-500">Processados OK</dt><dd className="font-medium">{pedido.resumo.processed_ok}</dd></div>
          <div><dt className="text-gray-500">Com adicional</dt><dd className="font-medium">{pedido.resumo.items_with_additional}</dd></div>
          <div><dt className="text-gray-500">Tempo</dt><dd className="font-medium">{pedido.processing_time_seconds}s</dd></div>
        </dl>
      )}
      <div className="flex gap-3 pt-1">
        <a
          href={`/pedidos/${pedido.id}/resultado`}
          download
          className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg font-medium hover:bg-blue-700"
        >
          Baixar Resultado
        </a>
        <button
          onClick={onNovo}
          className="px-4 py-2 border border-gray-300 text-sm rounded-lg hover:bg-gray-50"
        >
          Novo Pedido
        </button>
      </div>
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState(0)
  const [pedidoCriado, setPedidoCriado] = useState(null)
  const [refreshHistorico, setRefreshHistorico] = useState(0)

  function handleSuccess(pedido) {
    setPedidoCriado(pedido)
    setRefreshHistorico(r => r + 1)
  }

  function handleNovo() {
    setPedidoCriado(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="max-w-3xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-lg font-bold text-gray-900">PedidoBK</h1>
            <p className="text-xs text-gray-400">Gestão de Pedidos</p>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200 px-6">
        <div className="max-w-3xl mx-auto flex gap-6">
          {TABS.map((t, i) => (
            <button
              key={t}
              onClick={() => { setTab(i); if (i === 0) handleNovo() }}
              className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                tab === i
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <main className="max-w-3xl mx-auto px-6 py-8">
        {tab === 0 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h2 className="text-base font-semibold text-gray-800 mb-5">Processar Pedido</h2>
            {pedidoCriado
              ? <SucessoBanner pedido={pedidoCriado} onNovo={handleNovo} />
              : <UploadForm onSuccess={handleSuccess} />
            }
          </div>
        )}

        {tab === 1 && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-base font-semibold text-gray-800">Histórico de Pedidos</h2>
              <button
                onClick={() => setRefreshHistorico(r => r + 1)}
                className="text-sm text-gray-400 hover:text-gray-600"
              >
                ↻ Atualizar
              </button>
            </div>
            <Historico refresh={refreshHistorico} />
          </div>
        )}
      </main>
    </div>
  )
}
