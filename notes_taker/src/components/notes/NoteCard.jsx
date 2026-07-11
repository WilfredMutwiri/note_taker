import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Trash2 } from 'lucide-react'
import ConditionPills from './ConditionPills'
import SourceBadge from './SourceBadge'
import VerificationBadge from './VerificationBadge'
import ConfirmDialog from '../common/ConfirmDialog'
import { useNotes } from '../../context/NotesContext'
import { useToast } from '../../context/ToastContext'

export default function NoteCard({ note }) {
  const { deleteNote } = useNotes()
  const { showError } = useToast()
  const [confirmOpen, setConfirmOpen] = useState(false)

  function handleDeleteClick(event) {
    event.preventDefault()
    event.stopPropagation()
    setConfirmOpen(true)
  }

  async function handleConfirm() {
    setConfirmOpen(false)
    try {
      await deleteNote(note.id)
    } catch (error) {
      showError('Could not delete note', error.message)
    }
  }

  return (
    <>
      <Link
        to={`/notes/${note.id}`}
        className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 transition-shadow hover:shadow-md"
      >
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-base font-semibold text-ink">{note.title}</h3>
          <div className="flex shrink-0 items-center gap-1.5">
            <SourceBadge source={note.source} />
            <button
              type="button"
              onClick={handleDeleteClick}
              aria-label={`Delete ${note.title}`}
              className="rounded-md p-1 text-red-600 transition-colors hover:bg-red-50 hover:text-red-700"
            >
              <Trash2 className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
        <VerificationBadge verification={note.verification} note={note.verificationNote} />
        <p className="line-clamp-2 text-sm text-ink-muted">{note.summary}</p>
        <ConditionPills
          conditions={note.type === 'disease' ? note.superiorFoods : note.conditions}
          limit={3}
        />
      </Link>

      <ConfirmDialog
        open={confirmOpen}
        title="Delete this note?"
        description={`"${note.title}" will be permanently removed. This can't be undone.`}
        confirmLabel="Delete"
        onConfirm={handleConfirm}
        onCancel={() => setConfirmOpen(false)}
      />
    </>
  )
}
