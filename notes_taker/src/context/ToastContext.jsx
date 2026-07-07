import { createContext, useCallback, useContext, useState } from 'react'
import ToastViewport from '../components/common/ToastViewport'

const ToastContext = createContext(null)

let nextId = 1

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }, [])

  const showError = useCallback(
    (title, description) => {
      const id = nextId++
      setToasts((prev) => [...prev, { id, title, description }])
      setTimeout(() => dismissToast(id), 6000)
    },
    [dismissToast],
  )

  return (
    <ToastContext.Provider value={{ showError }}>
      {children}
      <ToastViewport toasts={toasts} onDismiss={dismissToast} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within a ToastProvider')
  return ctx
}
