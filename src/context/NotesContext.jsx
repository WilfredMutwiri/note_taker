import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import * as notesService from '../api/notesService'

const NotesContext = createContext(null)

export function NotesProvider({ children }) {
  const [notes, setNotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  const refresh = useCallback(async (query = '') => {
    setLoading(true)
    setError(null)
    try {
      const result = query ? await notesService.searchNotes(query) : await notesService.listNotes()
      setNotes(result)
    } catch {
      setError('Could not load notes. Please try again.')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const createNote = useCallback(async (payload) => {
    const note = await notesService.createNote(payload)
    setNotes((prev) => [note, ...prev])
    return note
  }, [])

  const uploadPdfNote = useCallback(async (file) => {
    const note = await notesService.uploadPdfNote(file)
    setNotes((prev) => [note, ...prev])
    return note
  }, [])

  const value = { notes, loading, error, refresh, createNote, uploadPdfNote }

  return <NotesContext.Provider value={value}>{children}</NotesContext.Provider>
}

export function useNotes() {
  const ctx = useContext(NotesContext)
  if (!ctx) throw new Error('useNotes must be used within a NotesProvider')
  return ctx
}
