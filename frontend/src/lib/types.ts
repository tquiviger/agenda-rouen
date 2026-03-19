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
  { label: string; color: string; bg: string; emoji: string }
> = {
  musique: { label: "Musique", color: "text-orange-700", bg: "bg-orange-100", emoji: "🎵" },
  spectacles: { label: "Spectacles", color: "text-pink-700", bg: "bg-pink-100", emoji: "🎭" },
  sport: { label: "Sport", color: "text-green-700", bg: "bg-green-100", emoji: "⚽" },
  expositions: { label: "Expositions", color: "text-purple-700", bg: "bg-purple-100", emoji: "🎨" },
  cinéma: { label: "Cinéma", color: "text-red-700", bg: "bg-red-100", emoji: "🎬" },
  festival: { label: "Festival", color: "text-yellow-700", bg: "bg-yellow-100", emoji: "🎉" },
  ateliers: { label: "Ateliers", color: "text-cyan-700", bg: "bg-cyan-100", emoji: "🛠️" },
  famille: { label: "Famille", color: "text-teal-700", bg: "bg-teal-100", emoji: "👨‍👩‍👧" },
  "vie-nocturne": { label: "Vie nocturne", color: "text-indigo-700", bg: "bg-indigo-100", emoji: "🌙" },
  autre: { label: "Autre", color: "text-gray-700", bg: "bg-gray-100", emoji: "📌" },
};

export type DateFilter = "all" | "today" | "week" | "weekend";
