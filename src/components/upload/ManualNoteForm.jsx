import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useNotes } from '../../context/NotesContext'
import Button from '../common/Button'

export default function ManualNoteForm() {
  const { createNote } = useNotes()
  const navigate = useNavigate()
  const [title, setTitle] = useState('')
  const [conditionsInput, setConditionsInput] = useState('')
  const [content, setContent] = useState('')
  const [submitting, setSubmitting] = useState(false)

  const canSubmit = title.trim() && content.trim() && !submitting

  async function handleSubmit(event) {
    event.preventDefault()
    if (!canSubmit) return

    setSubmitting(true)
    const conditions = conditionsInput
      .split(',')
      .map((c) => c.trim())
      .filter(Boolean)

    const note = await createNote({
      title: title.trim(),
      subject: title.trim(),
      conditions: conditions.length ? conditions : ['Uncategorized'],
      content: content.trim(),
    })
    navigate(`/notes/${note.id}`)
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div className="flex flex-col gap-1.5">
        <label htmlFor="title" className="text-sm font-medium text-ink">
          Title / food or remedy
        </label>
        <input
          id="title"
          value={title}
          onChange={(event) => setTitle(event.target.value)}
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
          onChange={(event) => setConditionsInput(event.target.value)}
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
          onChange={(event) => setContent(event.target.value)}
          rows={8}
          placeholder="Write what you know about this food/remedy..."
          className="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-ink focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
        />
      </div>

      <div>
        <Button type="submit" disabled={!canSubmit}>
          {submitting ? 'Saving...' : 'Save note'}
        </Button>
      </div>
    </form>
  )
}
