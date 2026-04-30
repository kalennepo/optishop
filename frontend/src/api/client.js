import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (email, password, role = 'shopper') =>
  api.post('/auth/register', { email, password, role });

export const login = (email, password) =>
  api.post('/auth/login', { email, password });

// Stores
export const createStore = (name, width, height) =>
  api.post('/stores/', { name, width, height });

export const getStoreLayout = (storeId) =>
  api.get(`/stores/${storeId}/layout`);

export const addAisle = (storeId, data) =>
  api.post(`/stores/${storeId}/aisles`, data);

export const updateAisle = (aisleId, data) =>
  api.put(`/stores/aisles/${aisleId}`, data);

export const deleteAisle = (aisleId) =>
  api.delete(`/stores/aisles/${aisleId}`);

export const addItem = (aisleId, name, pos_x, pos_y) =>
  api.post(`/stores/aisles/${aisleId}/items`, { name, pos_x, pos_y });

export const updateItem = (itemId, data) =>
  api.put(`/stores/items/${itemId}`, data);

export const deleteItem = (itemId) =>
  api.delete(`/stores/items/${itemId}`);

export const reportOutOfStock = (itemId) =>
  api.post(`/stores/items/${itemId}/report-out-of-stock`);

export const getOutOfStockItems = (storeId) =>
  api.get(`/stores/${storeId}/reports/out-of-stock`);

export const exportStore = (storeId) =>
  api.get(`/stores/${storeId}/export`);

export const importStore = (data) =>
  api.post('/stores/import', data);

// Route optimization
export const optimizeRoute = (store_id, item_names, entrance = [1.0, 1.0], exit_pos = [1.0, 1.0]) =>
  api.post('/route/optimize', { store_id, item_names, entrance, exit_pos });

// Carts
export const createCart = (name, is_favorite = false) =>
  api.post('/carts/', { name, is_favorite });

export const getFavoriteCarts = () =>
  api.get('/carts/favorites');

export const favoriteCart = (cartId, name) =>
  api.post(`/carts/${cartId}/favorite`, { name });

export const deleteFavoriteCart = (cartId) =>
  api.delete(`/carts/favorites/${cartId}`);

export const addItemToCart = (cartId, item_id) =>
  api.post(`/carts/${cartId}/items`, { item_id });

export const removeItemFromCart = (cartId, itemId) =>
  api.delete(`/carts/${cartId}/items/${itemId}`);

export default api;
