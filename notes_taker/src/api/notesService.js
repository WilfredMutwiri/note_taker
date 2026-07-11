// const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// test-redeployment

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL


function extractErrorMessage(body) {
  if (!body) return null
  if (typeof body.detail === 'string') return body.detail
  const fieldErrors = Object.entries(body).map(([field, messages]) => {
    const text = Array.isArray(messages) ? messages.join(' ') : String(messages)
    return `${field}: ${text}`
  })
  return fieldErrors.length ? fieldErrors.join(' ') : null
}

async function request(path, options) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, options)
  } catch {
    throw new Error('Could not reach the server. Check that the backend is running and try again.')
  }

  if (!response.ok) {
    const body = await response.json().catch(() => null)
    const error = new Error(
      extractErrorMessage(body) || `Something went wrong on the server (error ${response.status}).`,
    )
    error.status = response.status
    throw error
  }
  if (response.status === 204) return null
  return response.json()
}

export async function listNotes() {
  return request('/notes/')
}

export async function searchNotes(query) {
  const params = new URLSearchParams({ q: query })
  return request(`/notes/?${params}`)
}

export async function getNote(id) {
  try {
    return await request(`/notes/${id}/`)
  } catch (error) {
    if (error.status === 404) return null
    throw error
  }
}

export async function createNote({ title, subject, conditions, content }) {
  return request('/notes/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, subject, conditions, content }),
  })
}

export async function uploadPdfNote(file) {
  const formData = new FormData()
  formData.append('file', file)
  return request('/notes/upload_pdf/', {
    method: 'POST',
    body: formData,
  })
}

export async function deleteNote(id) {
  return request(`/notes/${id}/`, { method: 'DELETE' })
}

export async function regenerateNote(id) {
  return request(`/notes/${id}/regenerate/`, { method: 'POST' })
}
