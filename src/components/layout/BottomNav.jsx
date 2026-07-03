import { NavLink } from 'react-router-dom'
import { LayoutDashboard, NotebookText, PlusCircle } from 'lucide-react'

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/notes', label: 'Notes', icon: NotebookText },
  { to: '/notes/new', label: 'New Note', icon: PlusCircle },
]

export default function BottomNav() {
  return (
    <nav className="fixed inset-x-0 bottom-0 z-10 flex border-t border-border bg-surface pb-[env(safe-area-inset-bottom)] md:hidden">
      {links.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          className={({ isActive }) =>
            `flex flex-1 flex-col items-center gap-0.5 py-2.5 text-xs font-medium transition-colors ${
              isActive ? 'text-primary-600' : 'text-ink-muted'
            }`
          }
        >
          <Icon className="h-5 w-5" />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}
