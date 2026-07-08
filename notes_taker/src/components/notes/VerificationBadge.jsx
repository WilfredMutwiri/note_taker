import { CircleCheck, Sparkles } from 'lucide-react'
import Badge from '../common/Badge'

export default function VerificationBadge({ verification, note }) {
  if (verification === 'ai_research') {
    return (
      <Badge tone="warning" className="gap-1" title={note || undefined}>
        <Sparkles className="h-3 w-3" />
        AI research — not verified locally
      </Badge>
    )
  }

  if (verification === 'ai_corrected') {
    return (
      <Badge tone="warning" className="gap-1" title={note || undefined}>
        <Sparkles className="h-3 w-3" />
        AI-corrected
      </Badge>
    )
  }

  if (verification === 'web_confirmed') {
    return (
      <Badge tone="health" className="gap-1">
        <CircleCheck className="h-3 w-3" />
        Web-verified
      </Badge>
    )
  }

  return null
}
