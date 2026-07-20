export default function BulletList({ items }) {
  if (!items?.length) return null

  return (
    <ul className="flex flex-col gap-1 text-sm text-ink">
      {items.map((item) => (
        <li key={item} className="flex gap-2">
          <span className="text-ink-muted">&bull;</span>
          <span>{item}</span>
        </li>
      ))}
    </ul>
  )
}
