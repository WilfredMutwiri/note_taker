// Mock service standing in for the future Django REST API.
// Every function is async and returns plain data, so callers (NotesContext)
// don't need to change when this is swapped for real `fetch` calls.

import { notesStore, generateId } from './mockData'

const LATENCY_MS = 400

function delay(value, ms = LATENCY_MS) {
  return new Promise((resolve) => setTimeout(() => resolve(value), ms))
}

function sortByNewest(notes) {
  return [...notes].sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
}

export async function listNotes() {
  return delay(sortByNewest(notesStore))
}

export async function searchNotes(query) {
  const q = query.trim().toLowerCase()
  if (!q) return listNotes()

  const results = notesStore.filter((note) => {
    return (
      note.title.toLowerCase().includes(q) ||
      note.subject.toLowerCase().includes(q) ||
      note.conditions.some((c) => c.toLowerCase().includes(q))
    )
  })
  return delay(sortByNewest(results))
}

export async function getNote(id) {
  const note = notesStore.find((n) => String(n.id) === String(id))
  return delay(note ?? null)
}

export async function createNote({ title, subject, conditions, content }) {
  const note = {
    id: generateId(),
    title,
    subject,
    type: 'food',
    conditions,
    summary: content.slice(0, 220),
    content,
    source: 'manual',
    createdAt: new Date().toISOString(),
  }
  notesStore.push(note)
  return delay(note)
}

// Simulates handing a PDF to the AI summarization pipeline. In the real
// backend this uploads to Cloudflare R2 and queues an OpenAI summarization
// job; here it just fabricates a placeholder "AI-summarized" note so the
// upload flow is fully clickable end to end.
export async function uploadPdfNote(file) {
  const title = file.name.replace(/\.pdf$/i, '')
  const note = {
    id: generateId(),
    title,
    subject: title,
    type: 'food',
    conditions: ['Pending AI review'],
    summary:
      'This note was generated from an uploaded PDF. Once connected to the backend, the AI will read the document and replace this placeholder with a structured summary.',
    content: `Uploaded file: ${file.name}. Awaiting AI summarization once the backend pipeline is connected.`,
    source: 'pdf',
    createdAt: new Date().toISOString(),
  }
  notesStore.push(note)
  return delay(note, 900)
}
