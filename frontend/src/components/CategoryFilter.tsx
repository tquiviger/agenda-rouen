"use client";

import { CATEGORY_CONFIG, type Category } from "@/lib/types";

interface Props {
  selected: Category | null;
  onSelect: (cat: Category | null) => void;
}

const categories = Object.entries(CATEGORY_CONFIG) as [Category, (typeof CATEGORY_CONFIG)[Category]][];

export default function CategoryFilter({ selected, onSelect }: Props) {
  return (
    <div className="overflow-x-auto -mx-4 px-4 sm:-mx-6 sm:px-6 scrollbar-hide">
      <div className="flex gap-2 pb-1 w-max">
        <button
          onClick={() => onSelect(null)}
          className={`shrink-0 rounded-full px-3.5 py-1.5 text-xs sm:text-sm font-medium transition-all ${
            selected === null
              ? "bg-gray-900 text-white shadow-md"
              : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
          }`}
        >
          Tous
        </button>
        {categories.map(([key, config]) => (
          <button
            key={key}
            onClick={() => onSelect(selected === key ? null : key)}
            className={`shrink-0 rounded-full px-3.5 py-1.5 text-xs sm:text-sm font-medium transition-all ${
              selected === key
                ? `${config.bg} ${config.color} shadow-md ring-2 ring-current/20`
                : "bg-white text-gray-600 hover:bg-gray-100 border border-gray-200"
            }`}
          >
            {config.emoji} {config.label}
          </button>
        ))}
      </div>
    </div>
  );
}
