import { useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Search } from 'lucide-react'

export default function TopSearchBar() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const [value, setValue] = useState(searchParams.get('q') ?? '')

  function handleSubmit(event) {
    event.preventDefault()
    const query = value.trim()
    navigate(query ? `/notes?q=${encodeURIComponent(query)}` : '/notes')
  }

  return (
    <form onSubmit={handleSubmit} className="relative w-full max-w-md">
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-ink-muted" />
      <input
        type="search"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Search a food, remedy, or condition..."
        className="w-full rounded-lg border border-border bg-surface-muted py-2 pl-9 pr-3 text-sm text-ink placeholder:text-ink-muted focus:border-primary-400 focus:outline-none focus:ring-2 focus:ring-primary-200"
      />
    </form>
  )
}
