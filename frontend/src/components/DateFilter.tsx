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
    <div className="flex gap-1 rounded-xl bg-gray-100 p-1 w-full">
      {OPTIONS.map(({ value, label }) => (
        <button
          key={value}
          onClick={() => onSelect(value)}
          className={`flex-1 rounded-lg px-2 py-2 text-xs sm:text-sm font-medium transition-all whitespace-nowrap ${
            selected === value
              ? "bg-white text-gray-900 shadow-sm"
              : "text-gray-500 hover:text-gray-700"
          }`}
        >
          {label}
        </button>
      ))}
    </div>
  );
}
