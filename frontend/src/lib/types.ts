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
  musique:        { label: "Musique",      color: "#c2410c", bg: "#fff7ed",  darkBg: "#431407", darkColor: "#fdba74", emoji: "🎵", gradient: "from-orange-500 to-amber-500" },
  spectacles:     { label: "Spectacles",   color: "#be185d", bg: "#fdf2f8",  darkBg: "#500724", darkColor: "#f9a8d4", emoji: "🎭", gradient: "from-pink-500 to-rose-500" },
  sport:          { label: "Sport",        color: "#15803d", bg: "#f0fdf4",  darkBg: "#052e16", darkColor: "#86efac", emoji: "⚽", gradient: "from-green-500 to-emerald-500" },
  expositions:    { label: "Expositions",  color: "#7e22ce", bg: "#faf5ff",  darkBg: "#3b0764", darkColor: "#d8b4fe", emoji: "🎨", gradient: "from-purple-500 to-violet-500" },
  "cinéma":       { label: "Cinéma",       color: "#b91c1c", bg: "#fef2f2",  darkBg: "#450a0a", darkColor: "#fca5a5", emoji: "🎬", gradient: "from-red-500 to-rose-600" },
  festival:       { label: "Festival",     color: "#a16207", bg: "#fefce8",  darkBg: "#422006", darkColor: "#fde047", emoji: "🎉", gradient: "from-yellow-500 to-amber-500" },
  ateliers:       { label: "Ateliers",     color: "#0e7490", bg: "#ecfeff",  darkBg: "#083344", darkColor: "#67e8f9", emoji: "🛠️", gradient: "from-cyan-500 to-teal-500" },
  famille:        { label: "Famille",      color: "#0f766e", bg: "#f0fdfa",  darkBg: "#042f2e", darkColor: "#5eead4", emoji: "👨‍👩‍👧", gradient: "from-teal-500 to-emerald-500" },
  "vie-nocturne": { label: "Vie nocturne", color: "#4338ca", bg: "#eef2ff",  darkBg: "#1e1b4b", darkColor: "#a5b4fc", emoji: "🌙", gradient: "from-indigo-500 to-violet-600" },
  autre:          { label: "Autre",        color: "#374151", bg: "#f3f4f6",  darkBg: "#1f2937", darkColor: "#d1d5db", emoji: "📌", gradient: "from-gray-500 to-slate-500" },
};

export type DateFilter = "all" | "today" | "week" | "weekend";
