export default function SPIIndicator({ value }: { value: number | null }) {
  if (value === null) return <span className="text-gray-400">—</span>;
  const color = value >= 0.95 ? 'text-green-600' : value >= 0.8 ? 'text-yellow-600' : 'text-red-600';
  const bg = value >= 0.95 ? 'bg-green-50' : value >= 0.8 ? 'bg-yellow-50' : 'bg-red-50';
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-sm font-semibold ${color} ${bg}`}>
      {value.toFixed(2)}
    </span>
  );
}
