import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import TopSearchBar from './TopSearchBar'
import BottomNav from './BottomNav'

export default function AppShell() {
  return (
    <div className="flex min-h-svh">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center gap-4 border-b border-border bg-surface px-6 py-3">
          <TopSearchBar />
        </header>
        <main className="flex-1 overflow-y-auto px-6 py-8 pb-24 md:pb-8">
          <div className="mx-auto w-full max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
      <BottomNav />
    </div>
  )
}
