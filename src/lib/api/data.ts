import "server-only";

import { api } from "./client";
import {
  buildTrendData,
  mapFulfillment,
  mapForecast,
  mapInventoryItem,
  mapOrder,
  mapProduct,
  mapRecommendation,
  mapUser,
} from "./mappers";

export async function getProductData() {
  const [productsResponse, categoriesResponse] = await Promise.all([
    api.getProducts({ limit: 100 }),
    api.getCategories(),
  ]);
  return productsResponse.items.map((product, index) =>
    mapProduct(product, categoriesResponse.items, index),
  );
}

export async function getInventoryData() {
  const [products, inventoryResponse] = await Promise.all([
    getProductData(),
    api.getInventory({ limit: 100 }),
  ]);
  return inventoryResponse.items.map((item) => mapInventoryItem(item, products));
}

export async function getOrderData() {
  const [ordersResponse, usersResult] = await Promise.allSettled([
    api.getOrders({ limit: 100 }),
    getAdminUserData(),
  ]);
  if (ordersResponse.status === "rejected") throw ordersResponse.reason;
  const users = usersResult.status === "fulfilled" ? usersResult.value : [];
  return ordersResponse.value.items.map((order) => mapOrder(order, users));
}

export async function getMyOrderData() {
  const response = await api.getMyOrders({ limit: 100 });
  return response.items.map((order) => mapOrder(order));
}

export async function getForecastData() {
  const [products, inventory, forecastsResponse] = await Promise.all([
    getProductData(),
    getInventoryData(),
    api.getForecasts({ limit: 100 }),
  ]);
  return forecastsResponse.items.map((forecast) => mapForecast(forecast, products, inventory));
}

export async function getFulfillmentData() {
  const response = await api.getFulfillment({ limit: 100 });
  return response.items.map(mapFulfillment);
}

export async function getRecommendationData() {
  const response = await api.getAIInsights({ limit: 100 });
  return response.items.map(mapRecommendation);
}

export async function getAdminUserData() {
  const [usersResponse, rolesResponse] = await Promise.all([
    api.getAdminUsers({ limit: 100 }),
    api.getAdminRoles(),
  ]);
  return usersResponse.items.map((user) => mapUser(user, rolesResponse.items));
}

export async function getAdminRoleData() {
  const response = await api.getAdminRoles();
  return response.items;
}

export async function getCurrentUserData() {
  const user = await api.getCurrentUser();
  return mapUser(user);
}

export async function getOperationsSnapshot() {
  const [products, inventory, orders, forecasts] = await Promise.all([
    getProductData(),
    getInventoryData(),
    getOrderData(),
    getForecastData(),
  ]);
  return {
    products,
    inventory,
    orders,
    forecasts,
    trendData: buildTrendData({ orders, inventory, forecasts }),
  };
}
