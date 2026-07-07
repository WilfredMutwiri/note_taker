import { useState } from 'react'
import ManualNoteForm from './ManualNoteForm'
import PdfUploadDropzone from './PdfUploadDropzone'

const tabs = [
  { id: 'manual', label: 'Type a note' },
  { id: 'pdf', label: 'Upload PDF' },
]

export default function NewNoteTabs() {
  const [active, setActive] = useState('manual')

  return (
    <div className="flex flex-col gap-6">
      <div className="flex gap-1 rounded-lg border border-border bg-surface-muted p-1 w-fit">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActive(tab.id)}
            className={`rounded-md px-4 py-1.5 text-sm font-medium transition-colors ${
              active === tab.id
                ? 'bg-surface text-ink shadow-sm'
                : 'text-ink-muted hover:text-ink'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {active === 'manual' ? <ManualNoteForm /> : <PdfUploadDropzone />}
    </div>
  )
}
