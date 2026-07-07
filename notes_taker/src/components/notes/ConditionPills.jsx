import Badge from '../common/Badge'

export default function ConditionPills({ conditions, limit }) {
  const shown = limit ? conditions.slice(0, limit) : conditions
  const remaining = limit ? conditions.length - shown.length : 0

  return (
    <div className="flex flex-wrap gap-1.5">
      {shown.map((condition) => (
        <Badge key={condition} tone="health">
          {condition}
        </Badge>
      ))}
      {remaining > 0 && <Badge>+{remaining} more</Badge>}
    </div>
  )
}
