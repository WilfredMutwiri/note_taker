import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { NotesProvider } from './context/NotesContext'
import AppShell from './components/layout/AppShell'
import DashboardPage from './pages/DashboardPage'
import NotesListPage from './pages/NotesListPage'
import NoteDetailPage from './pages/NoteDetailPage'
import NewNotePage from './pages/NewNotePage'

function App() {
  return (
    <BrowserRouter>
      <NotesProvider>
        <Routes>
          <Route element={<AppShell />}>
            <Route index element={<DashboardPage />} />
            <Route path="notes" element={<NotesListPage />} />
            <Route path="notes/new" element={<NewNotePage />} />
            <Route path="notes/:id" element={<NoteDetailPage />} />
          </Route>
        </Routes>
      </NotesProvider>
    </BrowserRouter>
  )
}

export default App
