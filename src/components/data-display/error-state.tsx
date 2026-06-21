import { AlertTriangle } from "lucide-react";

export function ErrorState({ title, message }: { title: string; message: string }) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-5">
      <div className="flex gap-3">
        <AlertTriangle className="mt-0.5 size-5 text-red-600" />
        <div>
          <h2 className="font-semibold text-red-950">{title}</h2>
          <p className="mt-1 text-sm leading-6 text-red-700">{message}</p>
        </div>
      </div>
    </div>
  );
}
