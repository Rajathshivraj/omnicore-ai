export type PageMeta = {
  offset: number;
  limit: number;
  count: number;
};

export type PaginatedResponse<T> = {
  items: T[];
  meta: PageMeta;
};

export type ApiErrorResponse = {
  error_code?: string;
  message?: string;
  details?: unknown;
  request_id?: string | null;
};

export type ApiCategory = {
  id: string;
  parent_id: string | null;
  name: string;
  slug: string;
  description: string | null;
  sort_order: number;
  status: string;
};

export type ApiProduct = {
  id: string;
  category_id: string;
  sku: string;
  name: string;
  slug: string;
  description: string | null;
  status: string;
  price_amount: string | number;
  currency: string;
  cost_amount: string | number | null;
  image_url: string | null;
  attributes: Record<string, unknown>;
};

export type ApiInventory = {
  id: string;
  product_id: string;
  location_code: string;
  stock_on_hand: number;
  stock_reserved: number;
  stock_available: number;
  reorder_point: number;
  reorder_quantity: number | null;
  inventory_status: string;
};

export type ApiOrderItem = {
  id: string;
  product_id: string;
  sku_snapshot: string;
  product_name_snapshot: string;
  quantity: number;
  unit_price_amount: string | number;
  line_total_amount: string | number;
};

export type ApiOrder = {
  id: string;
  order_number: string;
  customer_id: string;
  status: string;
  fulfillment_status: string;
  payment_status: string;
  subtotal_amount: string | number;
  tax_amount: string | number;
  shipping_amount: string | number;
  discount_amount: string | number;
  total_amount: string | number;
  currency: string;
  shipping_name: string | null;
  shipping_address: Record<string, unknown> | null;
  placed_at: string;
  fulfilled_at: string | null;
  cancelled_at: string | null;
  items: ApiOrderItem[];
};

export type ApiForecast = {
  id: string;
  product_id: string;
  forecast_period_start: string;
  forecast_period_end: string;
  predicted_demand: number;
  suggested_reorder_quantity: number;
  confidence_score: string | number | null;
  model_name: string;
  model_version: string;
  source_window_start: string | null;
  source_window_end: string | null;
  generated_at: string;
  status: string;
  failure_reason: string | null;
  reviewed_at: string | null;
  reviewed_by_id: string | null;
};

export type ApiFulfillment = {
  id: string;
  order_id: string;
  status: string;
  warehouse_code: string;
  tracking_reference: string | null;
  exception_reason: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
};

export type ApiAIInsight = {
  id: string;
  insight_type: string;
  status: string;
  title: string;
  summary: string;
  suggested_action: string | null;
  confidence_score: string | number | null;
  product_id: string | null;
  order_id: string | null;
  forecast_id: string | null;
  source_refs: Record<string, unknown>[];
  input_snapshot: Record<string, unknown>;
  model_name: string | null;
  model_version: string | null;
  generated_at: string;
  reviewed_at: string | null;
  reviewed_by_id: string | null;
};

export type ApiRole = {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  permissions: Record<string, unknown>;
  is_system: boolean;
};

export type ApiUser = {
  id: string;
  role_id?: string;
  email: string;
  full_name: string;
  phone: string | null;
  status: string;
  role?: {
    id: string;
    name: string;
    slug: string;
  };
};

export type ApiTokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};
