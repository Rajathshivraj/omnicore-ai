import type {
  ApiAIInsight,
  ApiCategory,
  ApiForecast,
  ApiFulfillment,
  ApiInventory,
  ApiOrder,
  ApiProduct,
  ApiRole,
  ApiUser,
} from "./contracts";
import type {
  ChartPoint,
  Forecast,
  FulfillmentRecord,
  InventoryItem,
  InventoryStatus,
  Order,
  OrderStatus,
  Product,
  ProductStatus,
  Recommendation,
  RecommendationStatus,
  User,
  UserRole,
} from "@/types/domain";

const fallbackImages = [
  "https://images.unsplash.com/photo-1551028719-00167b16eac5?auto=format&fit=crop&w=900&q=80",
  "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?auto=format&fit=crop&w=900&q=80",
  "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=900&q=80",
  "https://images.unsplash.com/photo-1602143407151-7111542de6e8?auto=format&fit=crop&w=900&q=80",
];

function money(value: string | number | null | undefined) {
  return Number(value ?? 0);
}

function titleize(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function productStatus(value: string): ProductStatus {
  const status = titleize(value) as ProductStatus;
  return status;
}

function inventoryStatus(value: string): InventoryStatus {
  return titleize(value) as InventoryStatus;
}

function orderStatus(value: string): OrderStatus {
  return titleize(value) as OrderStatus;
}

function recommendationStatus(value: string): RecommendationStatus {
  return titleize(value) as RecommendationStatus;
}

function roleName(value: string): UserRole {
  return titleize(value) as UserRole;
}

function formatDate(value: string | null) {
  if (!value) return "Not available";
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(new Date(value));
}

function categoryMap(categories: ApiCategory[]) {
  return new Map(categories.map((category) => [category.id, category.name]));
}

export function mapProduct(
  product: ApiProduct,
  categories: ApiCategory[],
  index = 0,
): Product {
  const attributes = Object.entries(product.attributes ?? {}).map(
    ([key, value]) => `${titleize(key)}: ${String(value)}`,
  );
  return {
    id: product.id,
    name: product.name,
    sku: product.sku,
    category: categoryMap(categories).get(product.category_id) ?? "Uncategorized",
    price: money(product.price_amount),
    status: productStatus(product.status),
    rating: 4.6,
    image: product.image_url ?? fallbackImages[index % fallbackImages.length],
    description: product.description ?? "No product description has been provided yet.",
    attributes,
  };
}

export function mapInventoryItem(
  item: ApiInventory,
  products: Product[],
): InventoryItem {
  const product = products.find((candidate) => candidate.id === item.product_id);
  return {
    id: item.id,
    productId: item.product_id,
    sku: product?.sku ?? "Unknown SKU",
    name: product?.name ?? "Unknown product",
    category: product?.category ?? "Uncategorized",
    location: item.location_code,
    onHand: item.stock_on_hand,
    reserved: item.stock_reserved,
    available: item.stock_available,
    reorderPoint: item.reorder_point,
    unitCost: product ? Math.round(product.price * 0.45) : 0,
    status: inventoryStatus(item.inventory_status),
  };
}

export function mapOrder(order: ApiOrder, users: User[] = []): Order {
  const customer = users.find((user) => user.id === order.customer_id);
  return {
    id: order.order_number,
    customer: customer?.name ?? order.shipping_name ?? "Customer",
    status: orderStatus(order.status),
    fulfillmentStatus: titleize(order.fulfillment_status) as Order["fulfillmentStatus"],
    total: money(order.total_amount),
    date: formatDate(order.placed_at),
    destination: String(order.shipping_address?.city ?? order.shipping_name ?? "Not available"),
    lines: order.items.map((line) => ({
      productName: line.product_name_snapshot,
      sku: line.sku_snapshot,
      quantity: line.quantity,
      unitPrice: money(line.unit_price_amount),
    })),
  };
}

export function mapForecast(
  forecast: ApiForecast,
  products: Product[],
  inventory: InventoryItem[],
): Forecast {
  const product = products.find((candidate) => candidate.id === forecast.product_id);
  const stock = inventory.find((item) => item.productId === forecast.product_id);
  return {
    sku: product?.sku ?? "Unknown SKU",
    productName: product?.name ?? "Unknown product",
    period: `${formatDate(forecast.forecast_period_start)} - ${formatDate(forecast.forecast_period_end)}`,
    predictedDemand: forecast.predicted_demand,
    currentAvailable: stock?.available ?? 0,
    suggestedReorderQuantity: forecast.suggested_reorder_quantity,
    confidence: money(forecast.confidence_score),
    modelVersion: forecast.model_version,
    generatedAt: formatDate(forecast.generated_at),
  };
}

export function mapRecommendation(insight: ApiAIInsight): Recommendation {
  return {
    id: insight.id,
    title: insight.title,
    impact: insight.summary,
    suggestedAction: insight.suggested_action ?? "Review recommendation context before taking action.",
    confidence: money(insight.confidence_score),
    status: recommendationStatus(insight.status),
    source: insight.source_refs.length > 0 ? `${insight.source_refs.length} source references` : "No source references",
  };
}

export function mapFulfillment(record: ApiFulfillment): FulfillmentRecord {
  return {
    id: record.id,
    orderId: record.order_id,
    status: titleize(record.status) as FulfillmentRecord["status"],
    warehouse: record.warehouse_code,
    trackingReference: record.tracking_reference,
    exceptionReason: record.exception_reason,
    updatedAt: formatDate(record.updated_at),
  };
}

export function mapUser(user: ApiUser, roles: ApiRole[] = []): User {
  const role = user.role?.name ?? roles.find((candidate) => candidate.id === user.role_id)?.name ?? "Customer";
  return {
    id: user.id,
    name: user.full_name,
    email: user.email,
    role: roleName(role.toLowerCase().replaceAll(" ", "_")),
    status: titleize(user.status) as User["status"],
    lastActive: "Not available",
  };
}

export function buildTrendData({
  orders,
  inventory,
  forecasts,
}: {
  orders: Order[];
  inventory: InventoryItem[];
  forecasts: Forecast[];
}): ChartPoint[] {
  const inventoryValue = inventory.reduce((sum, item) => sum + item.onHand * item.unitCost, 0);
  const orderRevenue = orders.reduce((sum, order) => sum + order.total, 0);
  const forecastDemand = forecasts.reduce((sum, forecast) => sum + forecast.predictedDemand, 0);
  return [
    { label: "Current", revenue: orderRevenue, orders: orders.length, inventory: inventoryValue, demand: forecastDemand, forecast: forecastDemand },
  ];
}
