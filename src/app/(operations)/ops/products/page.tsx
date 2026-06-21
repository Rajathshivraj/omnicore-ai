import { Plus } from "lucide-react";

import { PageHeader } from "@/components/layout/page-header";
import { Button } from "@/components/ui/button";
import { ProductManagement } from "@/features/operations/product-management";
import { EmptyState } from "@/components/data-display/empty-state";
import { ErrorState } from "@/components/data-display/error-state";
import { getProductData } from "@/lib/api/data";
import { getErrorMessage } from "@/lib/api/errors";
import type { Product } from "@/types/domain";

export default async function OpsProductsPage() {
  let products: Product[] = [];
  let error: string | null = null;

  try {
    products = await getProductData();
  } catch (caught) {
    error = getErrorMessage(caught);
  }

  return (
    <>
      <PageHeader
        title="Products"
        description="Manage product catalog records, SKUs, categories, status, and operational product detail."
        actions={<Button className="bg-teal-700 hover:bg-teal-800"><Plus /> Mock product</Button>}
      />
      {error ? (
        <ErrorState title="Products could not be loaded" message={error} />
      ) : products.length === 0 ? (
        <EmptyState title="No products found" description="Create product records in the backend to populate the catalog." />
      ) : (
        <ProductManagement products={products} />
      )}
    </>
  );
}
