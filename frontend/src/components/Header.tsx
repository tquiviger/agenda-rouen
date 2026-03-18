export default function Header({ eventCount }: { eventCount: number }) {
  return (
    <header className="text-center space-y-1">
      <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-gray-900">
        <span className="text-orange-500">Agenda</span> Rouen
      </h1>
      <p className="text-gray-400 text-base sm:text-lg">
        {eventCount} événement{eventCount > 1 ? "s" : ""} à venir
      </p>
    </header>
  );
}
