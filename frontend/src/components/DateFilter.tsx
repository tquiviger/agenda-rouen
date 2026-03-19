"use client";

import type { DateFilter as DateFilterType } from "@/lib/types";

interface Props {
  selected: DateFilterType;
  onSelect: (filter: DateFilterType) => void;
}

const OPTIONS: { value: DateFilterType; label: string }[] = [
  { value: "all", label: "Tout" },
  { value: "today", label: "Aujourd'hui" },
  { value: "week", label: "7 jours" },
  { value: "weekend", label: "Week-end" },
];

export default function DateFilter({ selected, onSelect }: Props) {
  return (
    <div
      className="flex gap-1 rounded-xl p-1 w-full"
      style={{ background: "var(--surface)" }}
    >
      {OPTIONS.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => onSelect(value)}
          className={`flex-1 rounded-lg px-2 py-2 text-xs sm:text-sm font-medium transition-all whitespace-nowrap ${
            selected === value
              ? "shadow-sm"
              : "hover:opacity-80"
          }`}
          style={
            selected === value
              ? { background: "var(--accent)", color: "#fff" }
              : { color: "var(--muted-strong)" }
          }
        >
          {label}
        </button>
      ))}
    </div>
  );
}
