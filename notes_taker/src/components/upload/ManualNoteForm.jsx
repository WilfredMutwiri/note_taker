import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Info } from 'lucide-react'
import { useNotes } from '../../context/NotesContext'
import { useToast } from '../../context/ToastContext'
import { useDraft } from '../../context/DraftContext'
import Button from '../common/Button'

export default function ManualNoteForm() {
  const { createNote } = useNotes()
  const { showError } = useToast()
  const { draft, updateDraft, clearDraft, wasRestored } = useDraft()
  const navigate = useNavigate()
  const [submitting, setSubmitting] = useState(false)

  const { title, conditionsInput, content } = draft
  const canSubmit = title.trim() && content.trim() && !submitting
  const hasDraftContent = Boolean(title || conditionsInput || content)

  async function handleSubmit(event) {
    event.preventDefault()
    if (!canSubmit) return

    setSubmitting(true)
    const conditions = conditionsInput
      .split(',')
      .map((c) => c.trim())
      .filter(Boolean)

    try {
      const note = await createNote({
        title: title.trim(),
        subject: title.trim(),
        conditions: conditions.length ? conditions : ['Uncategorized'],
        content: content.trim(),
      })
      clearDraft()
      navigate(`/notes/${note.id}`)
    } catch (error) {
      showError('Could not save note', error.message)
      setSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      {wasRestored && (
        <p className="flex items-center gap-1.5 rounded-lg bg-primary-50 px-3 py-2 text-xs text-primary-700">
          <Info className="h-3.5 w-3.5 shrink-0" />
          Continuing an unsaved draft from earlier.
        </p>
      )}

      <div className="flex flex-col gap-1.5">
        <label htmlFor="title" className="text-sm font-medium text-ink">
          Title / food or remedy
        </label>
        <input
          id="title"
          value={title}
          onChange={(event) => updateDraft({ title: event.target.value })}
          placeholder="e.g. Apple"
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="conditions" className="text-sm font-medium text-ink">
          Conditions it helps with
        </label>
        <input
          id="conditions"
          value={conditionsInput}
          onChange={(event) => updateDraft({ conditionsInput: event.target.value })}
          placeholder="Comma-separated, e.g. High cholesterol, Constipation"
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
        />
      </div>

      <div className="flex flex-col gap-1.5">
        <label htmlFor="content" className="text-sm font-medium text-ink">
          Notes
        </label>
        <textarea
          id="content"
          value={content}
          onChange={(event) => updateDraft({ content: event.target.value })}
          rows={8}
          placeholder="Write what you know about this food/remedy..."
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
        />
      </div>

      <div className="flex items-center gap-2">
        <Button type="submit" disabled={!canSubmit}>
          {submitting ? 'Saving...' : 'Save note'}
        </Button>
        {hasDraftContent && (
          <Button type="button" variant="ghost" onClick={clearDraft} disabled={submitting}>
            Discard draft
          </Button>
        )}
      </div>
    </form>
  )
}
