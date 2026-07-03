import { Link } from 'react-router-dom'
import ConditionPills from './ConditionPills'
import SourceBadge from './SourceBadge'

export default function NoteCard({ note }) {
  return (
    <Link
      to={`/notes/${note.id}`}
      className="flex flex-col gap-3 rounded-xl border border-border bg-surface p-4 transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-base font-semibold text-ink">{note.title}</h3>
        <SourceBadge source={note.source} />
      </div>
      <p className="line-clamp-2 text-sm text-ink-muted">{note.summary}</p>
      <ConditionPills conditions={note.conditions} limit={3} />
    </Link>
  )
}
