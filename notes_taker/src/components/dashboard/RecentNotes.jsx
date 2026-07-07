import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import { useNotes } from '../../context/NotesContext'
import NoteList from '../notes/NoteList'

export default function RecentNotes() {
  const { notes, loading, error } = useNotes()
  const recent = notes.slice(0, 6)
  const [open, setOpen] = useState(false)

  return (
    <div className="flex flex-col gap-4">
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className="flex w-full items-center justify-between text-left"
        aria-expanded={open}
      >
        <h2 className="text-lg font-semibold text-ink">Recent notes</h2>
        <ChevronDown
          className={`h-5 w-5 text-ink-muted transition-transform ${open ? 'rotate-180' : ''}`}
        />
      </button>
      {open && <NoteList notes={recent} loading={loading} error={error} />}
    </div>
  )
}
