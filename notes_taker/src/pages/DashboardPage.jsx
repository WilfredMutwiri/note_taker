import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Search, Stethoscope } from 'lucide-react'
import QuickActions from '../components/dashboard/QuickActions'
import RecentNotes from '../components/dashboard/RecentNotes'

export default function DashboardPage() {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')

  function handleSubmit(event) {
    event.preventDefault()
    const q = query.trim()
    navigate(q ? `/notes?q=${encodeURIComponent(q)}` : '/notes')
  }

  return (
    <div className="flex flex-col gap-10">
      <section className="flex flex-col items-center gap-6 rounded-2xl border border-border bg-surface px-6 py-14 text-center">
        <div className="flex items-center gap-2 text-primary-600">
          <Stethoscope className="h-6 w-6" />
          <span className="text-sm font-medium uppercase tracking-wide">Healnote</span>
        </div>
        <h1 className="max-w-xl text-2xl font-semibold text-ink">
          Your Notes Assistant !
        </h1>
        <form onSubmit={handleSubmit} className="relative w-full max-w-lg">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-ink-muted" />
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try 'apple' or 'high cholesterol'..."
            autoFocus
            className="w-full rounded-xl border border-border bg-surface-muted py-3 pl-12 pr-4 text-sm text-ink placeholder:text-ink-muted focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
          />
        </form>
        <QuickActions />
      </section>

      <RecentNotes />
    </div>
  )
}
