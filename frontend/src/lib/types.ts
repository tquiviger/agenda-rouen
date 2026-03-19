export type Category =
  | "musique"
  | "spectacles"
  | "sport"
  | "expositions"
  | "cinéma"
  | "festival"
  | "ateliers"
  | "famille"
  | "vie-nocturne"
  | "autre";

export interface Event {
  id: string;
  title: string;
  description: string;
  date_start: string;
  date_end: string | null;
  time: string;
  location: string;
  address: string;
  category: Category;
  tags: string[];
  urls: string[];
  image_url: string;
  sources: string[];
  classified_at: string;
}

export const CATEGORY_CONFIG: Record<
  Category,
  { label: string; color: string; bg: string; darkBg: string; darkColor: string; emoji: string; gradient: string }
> = {
  musique:        { label: "Musique",      color: "text-orange-700", bg: "bg-orange-100",  darkBg: "bg-orange-950", darkColor: "text-orange-300", emoji: "🎵", gradient: "from-orange-500 to-amber-500" },
  spectacles:     { label: "Spectacles",   color: "text-pink-700",   bg: "bg-pink-100",    darkBg: "bg-pink-950",   darkColor: "text-pink-300",   emoji: "🎭", gradient: "from-pink-500 to-rose-500" },
  sport:          { label: "Sport",        color: "text-green-700",  bg: "bg-green-100",   darkBg: "bg-green-950",  darkColor: "text-green-300",  emoji: "⚽", gradient: "from-green-500 to-emerald-500" },
  expositions:    { label: "Expositions",  color: "text-purple-700", bg: "bg-purple-100",  darkBg: "bg-purple-950", darkColor: "text-purple-300", emoji: "🎨", gradient: "from-purple-500 to-violet-500" },
  "cinéma":       { label: "Cinéma",       color: "text-red-700",    bg: "bg-red-100",     darkBg: "bg-red-950",    darkColor: "text-red-300",    emoji: "🎬", gradient: "from-red-500 to-rose-600" },
  festival:       { label: "Festival",     color: "text-yellow-700", bg: "bg-yellow-100",  darkBg: "bg-yellow-950", darkColor: "text-yellow-300", emoji: "🎉", gradient: "from-yellow-500 to-amber-500" },
  ateliers:       { label: "Ateliers",     color: "text-cyan-700",   bg: "bg-cyan-100",    darkBg: "bg-cyan-950",   darkColor: "text-cyan-300",   emoji: "🛠️", gradient: "from-cyan-500 to-teal-500" },
  famille:        { label: "Famille",      color: "text-teal-700",   bg: "bg-teal-100",    darkBg: "bg-teal-950",   darkColor: "text-teal-300",   emoji: "👨‍👩‍👧", gradient: "from-teal-500 to-emerald-500" },
  "vie-nocturne": { label: "Vie nocturne", color: "text-indigo-700", bg: "bg-indigo-100",  darkBg: "bg-indigo-950", darkColor: "text-indigo-300", emoji: "🌙", gradient: "from-indigo-500 to-violet-600" },
  autre:          { label: "Autre",        color: "text-gray-700",   bg: "bg-gray-100",    darkBg: "bg-gray-800",   darkColor: "text-gray-300",   emoji: "📌", gradient: "from-gray-500 to-slate-500" },
};

export type DateFilter = "all" | "today" | "week" | "weekend";
