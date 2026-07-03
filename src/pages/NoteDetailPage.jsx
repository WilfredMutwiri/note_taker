import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'
import * as notesService from '../api/notesService'
import ConditionPills from '../components/notes/ConditionPills'
import SourceBadge from '../components/notes/SourceBadge'
import Spinner from '../components/common/Spinner'
import EmptyState from '../components/common/EmptyState'

export default function NoteDetailPage() {
  const { id } = useParams()
  const [note, setNote] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    setLoading(true)
    notesService.getNote(id).then((result) => {
      if (active) {
        setNote(result)
        setLoading(false)
      }
    })
    return () => {
      active = false
    }
  }, [id])

  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner className="h-6 w-6" />
      </div>
    )
  }

  if (!note) {
    return <EmptyState title="Note not found" description="It may have been removed." />
  }

  return (
    <div className="flex flex-col gap-6">
      <Link to="/notes" className="flex w-fit items-center gap-1.5 text-sm text-ink-muted hover:text-ink">
        <ArrowLeft className="h-4 w-4" />
        Back to notes
      </Link>

      <div className="flex flex-col gap-4 rounded-xl border border-border bg-surface p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <h1 className="text-2xl font-semibold text-ink">{note.title}</h1>
          <SourceBadge source={note.source} />
        </div>

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
