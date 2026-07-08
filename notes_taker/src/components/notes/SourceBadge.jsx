import { FileText, Globe, PenLine } from 'lucide-react'
import Badge from '../common/Badge'

export default function SourceBadge({ source }) {
  if (source === 'pdf') {
    return (
      <Badge className="gap-1">
        <FileText className="h-3 w-3" />
        AI-summarized (PDF)
      </Badge>
    )
  }

  if (source === 'web') {
    return (
      <Badge className="gap-1">
        <Globe className="h-3 w-3" />
        Web research
      </Badge>
    )
  }

  return (
    <Badge className="gap-1">
      <PenLine className="h-3 w-3" />
      Manual
    </Badge>
  )
}
