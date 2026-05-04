import { useState, useEffect } from 'react';
import { getStoreLayout, optimizeRoute, createCart, getFavoriteCarts, favoriteCart, deleteFavoriteCart, reportOutOfStock } from '../api/client';
import StoreMap from '../components/StoreMap';
import ShoppingList from '../components/ShoppingList';

const KNOWN_STORE_IDS = [1, 2, 3, 4, 5];

export default function ShopperView() {
  const [storeId, setStoreId] = useState('');
  const [storeIdInput, setStoreIdInput] = useState('');
  const [store, setStore] = useState(null);
  const [storeLoading, setStoreLoading] = useState(false);
  const [storeError, setStoreError] = useState('');

  const [items, setItems] = useState([]);
  const [routeResult, setRouteResult] = useState(null);
  const [routeLoading, setRouteLoading] = useState(false);
  const [routeError, setRouteError] = useState('');

  const [reportedItems, setReportedItems] = useState(new Set());

  const [cartName, setCartName] = useState('');
  const [savingCart, setSavingCart] = useState(false);
  const [favoriteCarts, setFavoriteCarts] = useState([]);
  const [savedMsg, setSavedMsg] = useState('');

  const allStoreItems = store?.aisles?.flatMap((a) => a.items?.map((i) => i.name) ?? []) ?? [];

  const loadStore = async (id) => {
    if (!id) return;
    setStoreLoading(true);
    setStoreError('');
    setStore(null);
    setRouteResult(null);
    try {
      const res = await getStoreLayout(id);
      setStore(res.data);
      setStoreId(id);
    } catch {
      setStoreError(`Store #${id} not found or unavailable.`);
    } finally {
      setStoreLoading(false);
    }
  };

  const loadFavorites = async () => {
    try {
      const res = await getFavoriteCarts();
      setFavoriteCarts(res.data);
    } catch {
      // not critical
    }
  };

  useEffect(() => { loadFavorites(); }, []);

  const handleOptimize = async () => {
    if (!storeId || items.length === 0) return;
    setRouteLoading(true);
    setRouteError('');
    setRouteResult(null);
    try {
      const res = await optimizeRoute(Number(storeId), items);
      setRouteResult(res.data);
    } catch (err) {
      setRouteError(err.response?.data?.detail ?? 'Optimization failed. Check that your items exist in this store.');
    } finally {
      setRouteLoading(false);
    }
  };

  const handleSaveCart = async () => {
    if (!cartName.trim() || items.length === 0) return;
    setSavingCart(true);
    try {
      const cartRes = await createCart(cartName.trim(), true);
      setSavedMsg(`Cart "${cartName}" saved!`);
      setCartName('');
      loadFavorites();
      setTimeout(() => setSavedMsg(''), 3000);
    } catch {
      setSavedMsg('Failed to save cart.');
    } finally {
      setSavingCart(false);
    }
  };

  const handleReportOutOfStock = async (itemId) => {
    try {
      await reportOutOfStock(itemId);
      setReportedItems((prev) => new Set(prev).add(itemId));
    } catch {}
  };

  const handleDeleteFavorite = async (cartId) => {
    try {
      await deleteFavoriteCart(cartId);
      loadFavorites();
    } catch {}
  };

  return (
    <div className="flex flex-col lg:flex-row gap-0 h-[calc(100vh-56px)]">
      {/* Left sidebar */}
      <div className="lg:w-80 xl:w-96 flex-shrink-0 bg-white border-r border-gray-200 overflow-y-auto flex flex-col">
        <div className="p-4 border-b border-gray-100">
          <h2 className="text-base font-semibold text-gray-800 mb-3">Select Store</h2>
          <div className="flex gap-2">
            <input
              type="number"
              min={1}
              value={storeIdInput}
              onChange={(e) => setStoreIdInput(e.target.value)}
              placeholder="Store ID"
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              onClick={() => loadStore(storeIdInput)}
              disabled={storeLoading}
              className="bg-green-700 text-white px-3 py-2 rounded-lg text-sm hover:bg-green-800 transition-colors disabled:opacity-50"
            >
              Load
            </button>
          </div>
          {storeError && <p className="text-red-500 text-xs mt-2">{storeError}</p>}
          {store && (
            <div className="mt-2 text-xs text-gray-500">
              <span className="font-medium text-gray-700">{store.name}</span>
              {' '}— {store.width}×{store.height} units · {store.aisles?.length ?? 0} aisles · {allStoreItems.length} items
            </div>
          )}
        </div>

        <div className="p-4 border-b border-gray-100 flex-1">
          <h2 className="text-base font-semibold text-gray-800 mb-3">Shopping List</h2>
          <ShoppingList items={items} onChange={setItems} storeItems={allStoreItems} />

          {store && items.length > 0 && (
            <button
              onClick={handleOptimize}
              disabled={routeLoading}
              className="mt-4 w-full bg-green-700 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-800 transition-colors disabled:opacity-50"
            >
              {routeLoading ? 'Optimizing…' : 'Optimize Route'}
            </button>
          )}

          {routeError && (
            <div className="mt-3 bg-red-50 border border-red-200 text-red-700 text-xs px-3 py-2 rounded-lg">
              {routeError}
            </div>
          )}
        </div>

        {/* Route results */}
        {routeResult && (
          <div className="p-4 border-b border-gray-100">
            <h2 className="text-base font-semibold text-gray-800 mb-2">Optimized Order</h2>
            <p className="text-xs text-gray-500 mb-3">
              Total distance: <span className="font-semibold text-green-700">{routeResult.estimated_distance?.toFixed(1)} units</span>
              {' '}· {routeResult.total_steps} steps
            </p>
            <ol className="flex flex-col gap-1">
              {routeResult.optimized_order.map((name, i) => {
                const item = routeResult.optimized_items[i];
                const reported = item && reportedItems.has(item.id);
                return (
                  <li key={name} className="flex items-center gap-2 text-sm">
                    <span className="w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-bold flex-shrink-0">
                      {i + 1}
                    </span>
                    <span className="text-gray-700 flex-1">{name}</span>
                    {item && (
                      <button
                        onClick={() => handleReportOutOfStock(item.id)}
                        disabled={reported}
                        title="Report out of stock"
                        className="text-xs text-gray-400 hover:text-orange-500 disabled:text-orange-400 disabled:cursor-default transition-colors flex-shrink-0"
                      >
                        {reported ? 'Reported' : 'Out of stock?'}
                      </button>
                    )}
                  </li>
                );
              })}
            </ol>
          </div>
        )}

        {/* Save cart */}
        <div className="p-4">
          <h2 className="text-base font-semibold text-gray-800 mb-3">Save List as Favorite</h2>
          <div className="flex gap-2">
            <input
              type="text"
              value={cartName}
              onChange={(e) => setCartName(e.target.value)}
              placeholder="Cart name…"
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              onClick={handleSaveCart}
              disabled={savingCart || items.length === 0}
              className="bg-green-100 text-green-800 px-3 py-2 rounded-lg text-sm hover:bg-green-200 transition-colors disabled:opacity-50 font-medium"
            >
              Save
            </button>
          </div>
          {savedMsg && <p className="text-xs text-green-700 mt-2">{savedMsg}</p>}

          {favoriteCarts.length > 0 && (
            <div className="mt-3">
              <p className="text-xs font-medium text-gray-600 mb-2">Saved Carts</p>
              <ul className="flex flex-col gap-1">
                {favoriteCarts.map((cart) => (
                  <li key={cart.id} className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-xs">
                    <span className="text-gray-700">{cart.name}</span>
                    <button onClick={() => handleDeleteFavorite(cart.id)} className="text-gray-400 hover:text-red-500">✕</button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Map area */}
      <div className="flex-1 bg-gray-50 flex flex-col items-center justify-center p-6 overflow-auto">
        {!store && !storeLoading && (
          <div className="text-center text-gray-400">
            <div className="text-5xl mb-4">🛒</div>
            <p className="text-lg font-medium">Load a store to get started</p>
            <p className="text-sm mt-1">Enter a store ID on the left and click Load</p>
          </div>
        )}
        {storeLoading && <p className="text-gray-500">Loading store…</p>}
        {store && (
          <div className="flex flex-col items-center gap-4">
            <h3 className="text-lg font-semibold text-gray-700">{store.name}</h3>
            <StoreMap
              store={store}
              routePath={routeResult?.path_coordinates}
              highlightedItems={items}
              optimizedItems={routeResult?.optimized_items ?? []}
            />
            <div className="flex gap-4 text-xs text-gray-500">
              <span className="flex items-center gap-1">
                <span className="inline-block w-3 h-3 rounded-full bg-green-700"></span> Item
              </span>
              <span className="flex items-center gap-1">
                <span className="inline-block w-3 h-3 rounded-full bg-red-500"></span> On your list
              </span>
              <span className="flex items-center gap-1">
                <span className="inline-block w-3 h-3 rounded-full bg-blue-700"></span> Entrance/Exit
              </span>
              <span className="flex items-center gap-1">
                <svg width="20" height="6"><line x1="0" y1="3" x2="20" y2="3" stroke="#dc2626" strokeWidth="2" strokeDasharray="4 2"/></svg> Route
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
