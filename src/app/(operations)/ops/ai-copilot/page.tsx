import { DataTable } from "@/components/data-display/data-table";
import { ErrorState } from "@/components/data-display/error-state";
import { StatusBadge } from "@/components/data-display/status-badge";
import { PageHeader } from "@/components/layout/page-header";
import { CopilotChat } from "@/features/operations/copilot-chat";
import { getRecommendationData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { Recommendation } from "@/types/domain";

export default async function AiCopilotPage() {
  let recommendations: Recommendation[] = [];
  let error: string | null = null;

  try {
    recommendations = await getRecommendationData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  return (
    <>
      <PageHeader title="AI Copilot" description="ChatGPT-style interface with backend recommendation review records." />
      <div className="grid gap-4 xl:grid-cols-[1fr_420px]">
        <CopilotChat />
        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-950">AI Recommendations</h2>
          {error ? (
            <ErrorState title="Recommendations could not be loaded" message={error} />
          ) : (
            <DataTable
              columns={["Recommendation", "Status", "Confidence"]}
              rows={recommendations.map((rec) => [
                <div key="rec">
                  <p className="font-medium text-slate-950">{rec.title}</p>
                  <p className="mt-1 text-xs leading-5 text-slate-500">{rec.impact}</p>
                </div>,
                <StatusBadge key="status" status={rec.status} />,
                `${rec.confidence}%`,
              ])}
              emptyMessage="No AI recommendations found."
            />
          )}
        </section>
      </div>
    </>
  );
}
