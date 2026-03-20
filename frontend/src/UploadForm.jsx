import { useRef, useState } from 'react'
import { criarPedido } from './api'

const FileInput = ({ label, accept, file, onChange }) => {
  const ref = useRef()
  return (
    <div
      onClick={() => ref.current.click()}
      className="border-2 border-dashed border-gray-300 rounded-lg p-4 cursor-pointer hover:border-blue-400 transition-colors"
    >
      <input ref={ref} type="file" accept={accept} className="hidden" onChange={e => onChange(e.target.files[0])} />
      <p className="text-sm font-medium text-gray-600">{label}</p>
      {file
        ? <p className="mt-1 text-sm text-blue-600 truncate">{file.name}</p>
        : <p className="mt-1 text-xs text-gray-400">Clique para selecionar</p>
      }
    </div>
  )
}

export default function UploadForm({ onSuccess }) {
  const [pedidoPdf, setPedidoPdf] = useState(null)
  const [relatorioPdf, setRelatorioPdf] = useState(null)
  const [templateXlsx, setTemplateXlsx] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const pronto = pedidoPdf && relatorioPdf && templateXlsx

  async function handleSubmit(e) {
    e.preventDefault()
    if (!pronto) return
    setLoading(true)
    setError(null)
    try {
      const pedido = await criarPedido(pedidoPdf, relatorioPdf, templateXlsx)
      onSuccess(pedido)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <FileInput label="PDF do Pedido" accept=".pdf" file={pedidoPdf} onChange={setPedidoPdf} />
      <FileInput label="PDF do Relatório de Vendas" accept=".pdf" file={relatorioPdf} onChange={setRelatorioPdf} />
      <FileInput label="Template Excel (.xlsx)" accept=".xlsx" file={templateXlsx} onChange={setTemplateXlsx} />

      {error && (
        <div className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={!pronto || loading}
        className="w-full py-2.5 px-4 rounded-lg font-medium text-white transition-colors
          bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed"
      >
        {loading ? 'Processando...' : 'Processar Pedido'}
      </button>
    </form>
  )
}
