export type ProductStatus = "Active" | "Inactive" | "Archived";
export type InventoryStatus = "Healthy" | "Low Stock" | "Stockout Risk" | "Out of Stock";
export type OrderStatus = "Pending" | "Confirmed" | "Processing" | "Fulfilled" | "Cancelled";
export type FulfillmentStatus = "Ready to Pick" | "Picking" | "Packed" | "Shipped" | "Exception";
export type RecommendationStatus = "New" | "Reviewed" | "Accepted" | "Dismissed";
export type UserRole = "Customer" | "Inventory Manager" | "Warehouse Manager" | "Admin";

export type Product = {
  id: string;
  name: string;
  sku: string;
  category: string;
  price: number;
  status: ProductStatus;
  rating: number;
  image: string;
  description: string;
  attributes: string[];
};

export type InventoryItem = {
  id: string;
  productId: string;
  sku: string;
  name: string;
  category: string;
  location: string;
  onHand: number;
  reserved: number;
  available: number;
  reorderPoint: number;
  unitCost: number;
  status: InventoryStatus;
};

export type OrderLine = {
  productName: string;
  sku: string;
  quantity: number;
  unitPrice: number;
};

export type Order = {
  id: string;
  customer: string;
  status: OrderStatus;
  fulfillmentStatus: FulfillmentStatus;
  total: number;
  date: string;
  destination: string;
  lines: OrderLine[];
};

export type Forecast = {
  sku: string;
  productName: string;
  period: string;
  predictedDemand: number;
  currentAvailable: number;
  suggestedReorderQuantity: number;
  confidence: number;
  modelVersion: string;
  generatedAt: string;
};

export type Recommendation = {
  id: string;
  title: string;
  impact: string;
  suggestedAction: string;
  confidence: number;
  status: RecommendationStatus;
  source: string;
};

export type FulfillmentRecord = {
  id: string;
  orderId: string;
  status: FulfillmentStatus;
  warehouse: string;
  trackingReference: string | null;
  exceptionReason: string | null;
  updatedAt: string;
};

export type User = {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  status: "Active" | "Invited" | "Suspended";
  lastActive: string;
};

export type ChartPoint = {
  label: string;
  revenue: number;
  orders: number;
  inventory: number;
  demand?: number;
  forecast?: number;
};
