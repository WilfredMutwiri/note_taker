import PageHeader from '../components/common/PageHeader'
import NewNoteTabs from '../components/upload/NewNoteTabs'

export default function NewNotePage() {
  return (
    <div className="flex flex-col gap-6">
      <PageHeader
        title="New note"
        description="Type a note directly, or upload a PDF for the AI to summarize."
      />
      <NewNoteTabs />
    </div>
  )
}
