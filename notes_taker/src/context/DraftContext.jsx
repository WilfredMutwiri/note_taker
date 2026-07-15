import { createContext, useContext, useEffect, useState } from 'react'

const EMPTY_DRAFT = { title: '', conditionsInput: '', content: '' }
const STORAGE_KEY = 'healnote:new-note-draft'

const DraftContext = createContext(null)

function loadDraft() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return EMPTY_DRAFT
    return { ...EMPTY_DRAFT, ...JSON.parse(raw) }
  } catch {
    return EMPTY_DRAFT
  }
}

function isEmptyDraft(draft) {
  return !draft.title && !draft.conditionsInput && !draft.content
}

export function DraftProvider({ children }) {
  const [draft, setDraft] = useState(loadDraft)
  // Captured once at load — true only if a draft was actually restored from a previous
  // session, so the "continuing a draft" banner doesn't show for content typed just now.
  const [wasRestored, setWasRestored] = useState(() => !isEmptyDraft(draft))

  useEffect(() => {
    try {
      if (isEmptyDraft(draft)) {
        localStorage.removeItem(STORAGE_KEY)
      } else {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(draft))
      }
    } catch {
      // localStorage unavailable (private browsing, quota, etc.) — draft just won't persist.
    }
  }, [draft])

  function updateDraft(patch) {
    setDraft((prev) => ({ ...prev, ...patch }))
  }

  function clearDraft() {
    setDraft(EMPTY_DRAFT)
    setWasRestored(false)
  }

  return (
    <DraftContext.Provider value={{ draft, updateDraft, clearDraft, wasRestored }}>
      {children}
    </DraftContext.Provider>
  )
}

export function useDraft() {
  const ctx = useContext(DraftContext)
  if (!ctx) throw new Error('useDraft must be used within a DraftProvider')
  return ctx
}
