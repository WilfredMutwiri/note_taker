import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, RefreshCw, Trash2 } from 'lucide-react'
import * as notesService from '../api/notesService'
import { useNotes } from '../context/NotesContext'
import { useToast } from '../context/ToastContext'
import ConditionPills from '../components/notes/ConditionPills'
import SourceBadge from '../components/notes/SourceBadge'
import VerificationBadge from '../components/notes/VerificationBadge'
import Spinner from '../components/common/Spinner'
import EmptyState from '../components/common/EmptyState'
import ConfirmDialog from '../components/common/ConfirmDialog'

export default function NoteDetailPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { deleteNote, regenerateNote } = useNotes()
  const { showError } = useToast()
  const [note, setNote] = useState(null)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const [regenerating, setRegenerating] = useState(false)
  const [confirmOpen, setConfirmOpen] = useState(false)

  useEffect(() => {
    let active = true
    setLoading(true)
    setLoadError(null)
    notesService
      .getNote(id)
      .then((result) => {
        if (active) {
          setNote(result)
          setLoading(false)
        }
      })
      .catch((error) => {
        if (active) {
          setLoadError(error.message)
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [id])

  async function handleDelete() {
    setConfirmOpen(false)
    setDeleting(true)
    try {
      await deleteNote(note.id)
      navigate('/notes')
    } catch (error) {
      showError('Could not delete note', error.message)
      setDeleting(false)
    }
  }

  async function handleRegenerate() {
    setRegenerating(true)
    try {
      const updated = await regenerateNote(note.id)
      setNote(updated)
    } catch (error) {
      showError('Could not regenerate AI summary', error.message)
    } finally {
      setRegenerating(false)
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner className="h-6 w-6" />
      </div>
    )
  }

  if (loadError) {
    return <EmptyState title="Couldn't load this note" description={loadError} />
  }

  if (!note) {
    return <EmptyState title="Note not found" description="It may have been removed." />
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between gap-3">
        <Link to="/notes" className="flex w-fit items-center gap-1.5 text-sm text-ink-muted hover:text-ink">
          <ArrowLeft className="h-4 w-4" />
          Back to notes
        </Link>

        <div className="flex items-center gap-2">
          {note.source === 'pdf' && (
            <button
              type="button"
              onClick={handleRegenerate}
              disabled={regenerating}
              className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-medium text-ink transition-colors hover:bg-surface-muted disabled:opacity-50"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${regenerating ? 'animate-spin' : ''}`} />
              {regenerating ? 'Regenerating...' : 'Regenerate AI summary'}
            </button>
          )}
          <button
            type="button"
            onClick={() => setConfirmOpen(true)}
            disabled={deleting}
            className="inline-flex items-center gap-1.5 rounded-lg border border-border bg-surface px-3 py-1.5 text-sm font-medium text-red-600 transition-colors hover:bg-red-50 disabled:opacity-50"
          >
            <Trash2 className="h-3.5 w-3.5" />
            {deleting ? 'Deleting...' : 'Delete'}
          </button>
        </div>
      </div>

      <ConfirmDialog
        open={confirmOpen}
        title="Delete this note?"
        description={`"${note.title}" will be permanently removed. This can't be undone.`}
        confirmLabel="Delete"
        onConfirm={handleDelete}
        onCancel={() => setConfirmOpen(false)}
      />

      <div className="flex flex-col gap-4 rounded-xl border border-border bg-surface p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h1 className="text-2xl font-semibold text-ink">{note.title}</h1>
          <div className="flex flex-wrap items-center gap-1.5">
            <SourceBadge source={note.source} />
            <VerificationBadge verification={note.verification} note={note.verificationNote} />
          </div>
        </div>

        {note.verificationNote && (
          <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">
            {note.verificationNote}
          </p>
        )}

        <div>
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
            Helps with
          </h2>
          <ConditionPills conditions={note.conditions} />
        </div>

        <div>
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
            Summary
          </h2>
          <p className="text-sm text-ink">{note.summary}</p>
        </div>

        <div>
          <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-ink-muted">
            Full notes
          </h2>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-ink">{note.content}</p>
        </div>

        <p className="text-xs text-ink-muted">
          Added {new Date(note.createdAt).toLocaleDateString()}
        </p>
      </div>
    </div>
  )
}
