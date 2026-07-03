import { useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { PlusCircle } from 'lucide-react'
import { useNotes } from '../context/NotesContext'
import NoteList from '../components/notes/NoteList'
import PageHeader from '../components/common/PageHeader'
import Button from '../components/common/Button'

export default function NotesListPage() {
  const [searchParams] = useSearchParams()
  const query = searchParams.get('q') ?? ''
  const { notes, loading, refresh } = useNotes()

  useEffect(() => {
    refresh(query)
  }, [query, refresh])

  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title={query ? `Results for "${query}"` : 'All notes'}
        description={query ? `${notes.length} note(s) match this search.` : 'Everything in your notes library.'}
        actions={
          <Button to="/notes/new">
            <PlusCircle className="h-4 w-4" />
            New note
          </Button>
        }
      />
      <NoteList notes={notes} loading={loading} />
    </div>
  )
}
