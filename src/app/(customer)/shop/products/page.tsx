import { EmptyState } from "@/components/data-display/empty-state";
import { ErrorState } from "@/components/data-display/error-state";
import { PageHeader } from "@/components/layout/page-header";
import { ProductBrowser } from "@/features/customer/product-browser";
import { getProductData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { Product } from "@/types/domain";

export default async function ProductsPage() {
  let products: Product[] = [];
  let error: string | null = null;

  try {
    products = await getProductData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  const activeProducts = products.filter((product) => product.status === "Active");

  return (
    <main className="mx-auto max-w-7xl px-4 py-8">
      <PageHeader
        title="Products"
        description="Search the customer-facing product catalog with category filtering and detailed product views."
      />
      {error ? (
        <ErrorState title="Products could not be loaded" message={error} />
      ) : activeProducts.length === 0 ? (
        <EmptyState title="No active products" description="Active backend products will appear in this catalog." />
      ) : (
        <ProductBrowser products={activeProducts} />
      )}
    </main>
  );
}
