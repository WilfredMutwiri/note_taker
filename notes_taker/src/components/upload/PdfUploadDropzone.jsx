import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { FileText, UploadCloud } from 'lucide-react'
import { useNotes } from '../../context/NotesContext'
import { useToast } from '../../context/ToastContext'
import Spinner from '../common/Spinner'

export default function PdfUploadDropzone() {
  const { uploadPdfNote } = useNotes()
  const { showError } = useToast()
  const navigate = useNavigate()
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [isDragging, setIsDragging] = useState(false)
  const [processing, setProcessing] = useState(false)

  function pickFile(candidate) {
    if (!candidate) return
    if (candidate.type !== 'application/pdf') {
      showError('Unsupported file', 'Please choose a PDF file.')
      return
    }
    setFile(candidate)
  }

  async function handleUpload() {
    if (!file) return
    setProcessing(true)
    try {
      const note = await uploadPdfNote(file)
      navigate(`/notes/${note.id}`)
    } catch (error) {
      showError('File upload failed', error.message)
      setProcessing(false)
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <div
        onDragOver={(event) => {
          event.preventDefault()
          setIsDragging(true)
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(event) => {
          event.preventDefault()
          setIsDragging(false)
          pickFile(event.dataTransfer.files?.[0])
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition-colors ${
          isDragging ? 'border-primary-400 bg-primary-50' : 'border-border bg-surface-muted'
        }`}
      >
        <UploadCloud className="h-8 w-8 text-primary-600" />
        <p className="text-sm font-medium text-ink">
          Drag a PDF here, or click to browse
        </p>
        <p className="text-xs text-ink-muted">
          The AI will read the document and generate a structured summary note.
        </p>
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          className="hidden"
          onChange={(event) => pickFile(event.target.files?.[0])}
        />
      </div>

      {file && (
        <div className="flex items-center justify-between rounded-lg border border-border bg-surface p-3">
          <div className="flex items-center gap-2 text-sm text-ink">
            <FileText className="h-4 w-4 text-primary-600" />
            {file.name}
          </div>
          <button
            type="button"
            onClick={handleUpload}
            disabled={processing}
            className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
          >
            {processing && <Spinner className="h-4 w-4" color="text-white" />}
            {processing ? 'Processing...' : 'Upload & summarize'}
          </button>
        </div>
      )}
    </div>
  )
}
