"use client";

import { CATEGORY_CONFIG, type Category } from "@/lib/types";

interface Props {
  selected: Category | null;
  onSelect: (cat: Category | null) => void;
  counts: Record<string, number>;
}

const categories = Object.entries(CATEGORY_CONFIG) as [Category, (typeof CATEGORY_CONFIG)[Category]][];

export default function CategoryFilter({ selected, onSelect, counts }: Props) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0);

  return (
    <div className="overflow-x-auto -mx-4 px-4 sm:-mx-6 sm:px-6 scrollbar-hide">
      <div className="flex gap-2 pb-1 w-max">
        <button
          onClick={() => onSelect(null)}
          className="shrink-0 rounded-full px-3.5 py-1.5 text-xs sm:text-sm font-medium transition-all"
          style={
            selected === null
              ? { background: "var(--foreground)", color: "var(--background)" }
              : { background: "var(--surface)", color: "var(--muted-strong)", border: "1px solid var(--border)" }
          }
        >
          Tous{" "}
          <span className="opacity-60">{total}</span>
        </button>
        {categories.map(([key, config]) => {
          const count = counts[key] || 0;
          const isActive = selected === key;
          return (
            <button
              key={key}
              onClick={() => onSelect(isActive ? null : key)}
              className={`shrink-0 rounded-full px-3.5 py-1.5 text-xs sm:text-sm font-medium transition-all ${
                isActive
                  ? `${config.bg} ${config.color} dark:${config.darkBg} dark:${config.darkColor} shadow-md ring-2 ring-current/20`
                  : ""
              }`}
              style={
                isActive
                  ? undefined
                  : { background: "var(--surface)", color: "var(--muted-strong)", border: "1px solid var(--border)" }
              }
            >
              {config.emoji} {config.label}{" "}
              <span className="opacity-60">{count}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
