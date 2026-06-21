import { ChartCard } from "@/components/data-display/chart-card";
import { DataTable } from "@/components/data-display/data-table";
import { ErrorState } from "@/components/data-display/error-state";
import { PageHeader } from "@/components/layout/page-header";
import { buildTrendData } from "@/lib/api/mappers";
import { getForecastData, getInventoryData, getOrderData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { ChartPoint, Forecast } from "@/types/domain";

export default async function ForecastingPage() {
  let forecasts: Forecast[] = [];
  let trendData: ChartPoint[] = [];
  let error: string | null = null;

  try {
    const [forecastData, inventory, orders] = await Promise.all([
      getForecastData(),
      getInventoryData(),
      getOrderData(),
    ]);
    forecasts = forecastData;
    trendData = buildTrendData({ forecasts, inventory, orders });
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  if (error) {
    return (
      <>
        <PageHeader title="Forecasting" description="Demand forecasts with predicted demand and suggested reorder quantity." />
        <ErrorState title="Forecasting data could not be loaded" message={error} />
      </>
    );
  }

  return (
    <>
      <PageHeader title="Forecasting" description="Demand forecasts with predicted demand and suggested reorder quantity." />
      <ChartCard title="Demand Forecast Trend" data={trendData} dataKey="forecast" type="area" color="#0f766e" />
      <section className="mt-6">
        <DataTable
          columns={["SKU", "Product", "Period", "Predicted Demand", "Available", "Suggested Reorder", "Confidence", "Model"]}
          rows={forecasts.map((forecast) => [
            <span key="sku" className="font-medium text-slate-950">{forecast.sku}</span>,
            forecast.productName,
            forecast.period,
            forecast.predictedDemand,
            forecast.currentAvailable,
            <span key="reorder" className="font-semibold text-teal-700">{forecast.suggestedReorderQuantity}</span>,
            `${forecast.confidence}%`,
            forecast.modelVersion,
          ])}
          emptyMessage="No forecast records found."
        />
      </section>
    </>
  );
}
