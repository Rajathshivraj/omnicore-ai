export default function ShopLoading() {
  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <div className="h-8 w-56 rounded-md bg-slate-200" />
      <div className="mt-3 h-4 w-96 max-w-full rounded-md bg-slate-100" />
      <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 6 }).map((_, index) => (
          <div key={index} className="overflow-hidden rounded-lg border bg-white shadow-sm">
            <div className="h-56 bg-slate-100" />
            <div className="space-y-3 p-4">
              <div className="h-4 w-24 rounded bg-slate-100" />
              <div className="h-5 w-40 rounded bg-slate-200" />
              <div className="h-4 w-full rounded bg-slate-100" />
            </div>
          </div>
        ))}
      </div>
    </main>
  );
}
