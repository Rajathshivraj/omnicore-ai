export default function OpsLoading() {
  return (
    <div className="space-y-6">
      <div>
        <div className="h-7 w-48 rounded-md bg-slate-200" />
        <div className="mt-3 h-4 w-96 max-w-full rounded-md bg-slate-100" />
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-28 rounded-lg border bg-white p-4 shadow-sm">
            <div className="h-4 w-24 rounded bg-slate-100" />
            <div className="mt-4 h-7 w-20 rounded bg-slate-200" />
          </div>
        ))}
      </div>
      <div className="h-80 rounded-lg border bg-white shadow-sm" />
    </div>
  );
}
