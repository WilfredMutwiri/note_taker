import { Loader2 } from 'lucide-react'

export default function Spinner({ className = '', color = 'text-primary-600' }) {
  return <Loader2 className={`animate-spin ${color} ${className}`} />
}
