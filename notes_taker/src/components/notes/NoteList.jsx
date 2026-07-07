import { AlertTriangle, SearchX } from 'lucide-react'
import NoteCard from './NoteCard'
import EmptyState from '../common/EmptyState'
import Spinner from '../common/Spinner'

export default function NoteList({ notes, loading, error }) {
  if (loading) {
    return (
      <div className="flex justify-center py-16">
        <Spinner className="h-6 w-6" />
      </div>
    )
  }

  if (error) {
    return <EmptyState icon={AlertTriangle} title="Couldn't load notes" description={error} />
  }

  if (notes.length === 0) {
    return (
      <EmptyState
        icon={SearchX}
        title="No notes found"
        description="Try a different keyword, or add a new note to build up your library."
      />
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {notes.map((note) => (
        <NoteCard key={note.id} note={note} />
      ))}
    </div>
  )
}
