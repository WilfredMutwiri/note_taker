import { NotebookText, PlusCircle } from 'lucide-react'
import Button from '../common/Button'

export default function QuickActions() {
  return (
    <div className="flex flex-nowrap justify-center gap-2 sm:gap-3">
      <Button to="/notes/new" variant="primary">
        <PlusCircle className="h-4 w-4" />
        New note
      </Button>
      <Button to="/notes" variant="secondary">
        <NotebookText className="h-4 w-4" />
        Browse notes
      </Button>
    </div>
  )
}
