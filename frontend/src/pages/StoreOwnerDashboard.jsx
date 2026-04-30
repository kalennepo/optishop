import { useState, useEffect } from 'react';
import {
  createStore, getStoreLayout,
  addAisle, updateAisle, deleteAisle,
  addItem, updateItem, deleteItem,
  getOutOfStockItems, exportStore, importStore,
} from '../api/client';
import StoreMap from '../components/StoreMap';
import AisleEditor from '../components/AisleEditor';
import ItemEditor from '../components/ItemEditor';

const TABS = ['My Stores', 'Layout Editor', 'Out-of-Stock'];

export default function StoreOwnerDashboard() {
  const [tab, setTab] = useState('My Stores');

  // My Stores tab
  const [stores, setStores] = useState([]);
  const [newStoreName, setNewStoreName] = useState('');
  const [newStoreWidth, setNewStoreWidth] = useState('');
  const [newStoreHeight, setNewStoreHeight] = useState('');
  const [creatingStore, setCreatingStore] = useState(false);
  const [storeMsg, setStoreMsg] = useState('');

  // Layout Editor tab
  const [editorStoreId, setEditorStoreId] = useState('');
  const [editorStoreIdInput, setEditorStoreIdInput] = useState('');
  const [store, setStore] = useState(null);
  const [storeLoading, setStoreLoading] = useState(false);
  const [storeError, setStoreError] = useState('');

  const [showAddAisle, setShowAddAisle] = useState(false);
  const [editingAisle, setEditingAisle] = useState(null);
  const [showAddItem, setShowAddItem] = useState(false);
  const [editingItem, setEditingItem] = useState(null);
  const [clickedPos, setClickedPos] = useState(null);
  const [editorMsg, setEditorMsg] = useState('');

  // Import/Export
  const [importJson, setImportJson] = useState('');
  const [importMsg, setImportMsg] = useState('');

  // Out-of-stock tab
  const [oosStoreId, setOosStoreId] = useState('');
  const [oosStoreIdInput, setOosStoreIdInput] = useState('');
  const [oosItems, setOosItems] = useState([]);
  const [oosLoading, setOosLoading] = useState(false);
  const [oosError, setOosError] = useState('');

  const flash = (setter, msg, ms = 3000) => {
    setter(msg);
    setTimeout(() => setter(''), ms);
  };

  // ---- My Stores ----
  const handleCreateStore = async (e) => {
    e.preventDefault();
    setCreatingStore(true);
    try {
      const res = await createStore(newStoreName, Number(newStoreWidth), Number(newStoreHeight));
      setStores((prev) => [...prev, res.data]);
      setNewStoreName(''); setNewStoreWidth(''); setNewStoreHeight('');
      flash(setStoreMsg, `Store "${res.data.name}" created (ID: ${res.data.id})`);
    } catch (err) {
      flash(setStoreMsg, err.response?.data?.detail ?? 'Failed to create store.');
    } finally {
      setCreatingStore(false);
    }
  };

  // ---- Layout Editor ----
  const loadStore = async (id) => {
    if (!id) return;
    setStoreLoading(true);
    setStoreError('');
    setStore(null);
    try {
      const res = await getStoreLayout(id);
      setStore(res.data);
      setEditorStoreId(id);
    } catch {
      setStoreError(`Store #${id} not found.`);
    } finally {
      setStoreLoading(false);
    }
  };

  const refreshStore = () => loadStore(editorStoreId);

  const handleAddAisle = async (data) => {
    try {
      await addAisle(editorStoreId, data);
      setShowAddAisle(false);
      flash(setEditorMsg, 'Aisle added.');
      refreshStore();
    } catch (err) {
      flash(setEditorMsg, err.response?.data?.detail ?? 'Failed to add aisle.');
    }
  };

  const handleUpdateAisle = async (data) => {
    try {
      await updateAisle(editingAisle.id, data);
      setEditingAisle(null);
      flash(setEditorMsg, 'Aisle updated.');
      refreshStore();
    } catch (err) {
      flash(setEditorMsg, err.response?.data?.detail ?? 'Failed to update aisle.');
    }
  };

  const handleDeleteAisle = async (aisleId) => {
    if (!confirm('Delete this aisle and all its items?')) return;
    try {
      await deleteAisle(aisleId);
      flash(setEditorMsg, 'Aisle deleted.');
      refreshStore();
    } catch (err) {
      flash(setEditorMsg, err.response?.data?.detail ?? 'Failed to delete aisle.');
    }
  };

  const handleAddItem = async (data) => {
    try {
      await addItem(data.aisle_id, data.name, data.pos_x, data.pos_y);
      setShowAddItem(false);
      setClickedPos(null);
      flash(setEditorMsg, 'Item added.');
      refreshStore();
    } catch (err) {
      flash(setEditorMsg, err.response?.data?.detail ?? 'Failed to add item.');
    }
  };

  const handleUpdateItem = async (data) => {
    try {
      await updateItem(editingItem.id, { name: data.name, pos_x: data.pos_x, pos_y: data.pos_y, aisle_id: data.aisle_id });
      setEditingItem(null);
      flash(setEditorMsg, 'Item updated.');
      refreshStore();
    } catch (err) {
      flash(setEditorMsg, err.response?.data?.detail ?? 'Failed to update item.');
    }
  };

  const handleDeleteItem = async (itemId) => {
    if (!confirm('Delete this item?')) return;
    try {
      await deleteItem(itemId);
      flash(setEditorMsg, 'Item deleted.');
      refreshStore();
    } catch (err) {
      flash(setEditorMsg, err.response?.data?.detail ?? 'Failed to delete item.');
    }
  };

  const handleMapClick = (x, y) => {
    if (!store?.aisles?.length) return;
    setClickedPos([x, y]);
    setShowAddItem(true);
  };

  const handleItemMoved = async (itemId, newX, newY) => {
    try {
      await updateItem(itemId, { pos_x: newX, pos_y: newY });
      refreshStore();
    } catch {
      flash(setEditorMsg, 'Failed to save item position.');
    }
  };

  const handleAisleMoved = async (aisleId, x_min, y_min, x_max, y_max) => {
    try {
      await updateAisle(aisleId, { x_min, y_min, x_max, y_max });
      refreshStore();
    } catch {
      flash(setEditorMsg, 'Failed to save aisle position.');
    }
  };

  const handleExport = async () => {
    try {
      const res = await exportStore(editorStoreId);
      const blob = new Blob([JSON.stringify(res.data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `store_${editorStoreId}.json`; a.click();
      URL.revokeObjectURL(url);
    } catch {
      flash(setEditorMsg, 'Export failed.');
    }
  };

  const handleImport = async () => {
    try {
      const data = JSON.parse(importJson);
      const res = await importStore(data);
      flash(setImportMsg, `Imported as Store ID ${res.data.id}`);
      setImportJson('');
    } catch {
      flash(setImportMsg, 'Import failed. Check JSON format.');
    }
  };

  // ---- Out-of-stock ----
  const loadOos = async (id) => {
    setOosLoading(true);
    setOosError('');
    try {
      const res = await getOutOfStockItems(id);
      setOosItems(res.data);
      setOosStoreId(id);
    } catch {
      setOosError(`Store #${id} not found or no access.`);
    } finally {
      setOosLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-56px)]">
      {/* Tab bar */}
      <div className="bg-white border-b border-gray-200 px-6 flex gap-1 pt-3">
        {TABS.map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors ${
              tab === t ? 'border-green-700 text-green-700 bg-green-50' : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {/* ======== MY STORES ======== */}
        {tab === 'My Stores' && (
          <div className="max-w-lg">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Create New Store</h2>
            <form onSubmit={handleCreateStore} className="flex flex-col gap-3 bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Store Name</label>
                <input type="text" value={newStoreName} onChange={(e) => setNewStoreName(e.target.value)} required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" placeholder="e.g. Downtown Grocery" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Width (units)</label>
                  <input type="number" step="0.1" min="1" value={newStoreWidth} onChange={(e) => setNewStoreWidth(e.target.value)} required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Height (units)</label>
                  <input type="number" step="0.1" min="1" value={newStoreHeight} onChange={(e) => setNewStoreHeight(e.target.value)} required className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
                </div>
              </div>
              <button type="submit" disabled={creatingStore} className="w-full bg-green-700 text-white py-2 rounded-lg text-sm font-medium hover:bg-green-800 transition-colors disabled:opacity-50">
                {creatingStore ? 'Creating…' : 'Create Store'}
              </button>
            </form>
            {storeMsg && <p className="text-sm text-green-700 mt-3">{storeMsg}</p>}

            {stores.length > 0 && (
              <div className="mt-6">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">Created this session</h3>
                <ul className="flex flex-col gap-2">
                  {stores.map((s) => (
                    <li key={s.id} className="bg-white border border-gray-200 rounded-xl px-4 py-3 text-sm flex items-center justify-between">
                      <div>
                        <span className="font-medium text-gray-800">{s.name}</span>
                        <span className="text-gray-400 ml-2">ID: {s.id} · {s.width}×{s.height}</span>
                      </div>
                      <button
                        onClick={() => { setEditorStoreIdInput(String(s.id)); setTab('Layout Editor'); loadStore(s.id); }}
                        className="text-xs text-green-700 hover:underline"
                      >
                        Edit Layout →
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* ======== LAYOUT EDITOR ======== */}
        {tab === 'Layout Editor' && (
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Left panel */}
            <div className="lg:w-80 xl:w-96 flex-shrink-0 flex flex-col gap-4">
              <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">Load Store</h3>
                <div className="flex gap-2">
                  <input type="number" min={1} value={editorStoreIdInput} onChange={(e) => setEditorStoreIdInput(e.target.value)} placeholder="Store ID" className="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
                  <button onClick={() => loadStore(editorStoreIdInput)} disabled={storeLoading} className="bg-green-700 text-white px-3 py-1.5 rounded-lg text-sm hover:bg-green-800 transition-colors disabled:opacity-50">Load</button>
                </div>
                {storeError && <p className="text-red-500 text-xs mt-2">{storeError}</p>}
                {store && <p className="text-xs text-gray-500 mt-2"><span className="font-medium">{store.name}</span> — {store.width}×{store.height}</p>}
              </div>

              {store && (
                <>
                  {editorMsg && <div className="bg-green-50 border border-green-200 text-green-700 text-xs px-3 py-2 rounded-lg">{editorMsg}</div>}

                  {/* Aisles */}
                  <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-semibold text-gray-700">Aisles</h3>
                      <button onClick={() => { setShowAddAisle(true); setEditingAisle(null); }} className="text-xs text-green-700 hover:underline">+ Add</button>
                    </div>

                    {showAddAisle && !editingAisle && (
                      <div className="mb-3">
                        <AisleEditor onSave={handleAddAisle} onCancel={() => setShowAddAisle(false)} />
                      </div>
                    )}

                    <ul className="flex flex-col gap-1">
                      {store.aisles?.map((aisle) => (
                        <li key={aisle.id}>
                          {editingAisle?.id === aisle.id ? (
                            <AisleEditor initial={aisle} onSave={handleUpdateAisle} onCancel={() => setEditingAisle(null)} />
                          ) : (
                            <div className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-xs">
                              <span className="font-medium text-gray-700">{aisle.name}</span>
                              <div className="flex gap-2">
                                <button onClick={() => { setEditingAisle(aisle); setShowAddAisle(false); }} className="text-blue-600 hover:underline">Edit</button>
                                <button onClick={() => handleDeleteAisle(aisle.id)} className="text-red-500 hover:underline">Delete</button>
                              </div>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Items */}
                  <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-sm font-semibold text-gray-700">Items</h3>
                      <button onClick={() => { setShowAddItem(true); setEditingItem(null); setClickedPos(null); }} className="text-xs text-green-700 hover:underline">+ Add</button>
                    </div>
                    <p className="text-xs text-gray-400 mb-3">Tip: click on the map to place an item at a position</p>

                    {(showAddItem && !editingItem) && store.aisles?.length > 0 && (
                      <div className="mb-3">
                        <ItemEditor aisles={store.aisles} clickedPos={clickedPos} onSave={handleAddItem} onCancel={() => { setShowAddItem(false); setClickedPos(null); }} />
                      </div>
                    )}

                    <ul className="flex flex-col gap-1 max-h-48 overflow-y-auto">
                      {store.aisles?.flatMap((aisle) =>
                        aisle.items?.map((item) => (
                          <li key={item.id}>
                            {editingItem?.id === item.id ? (
                              <ItemEditor aisles={store.aisles} initial={{ ...item, aisle_id: aisle.id }} onSave={handleUpdateItem} onCancel={() => setEditingItem(null)} />
                            ) : (
                              <div className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-xs">
                                <div>
                                  <span className="font-medium text-gray-700">{item.name}</span>
                                  <span className="text-gray-400 ml-1">({(item.pos_x ?? item.x)?.toFixed(1)}, {(item.pos_y ?? item.y)?.toFixed(1)})</span>
                                </div>
                                <div className="flex gap-2">
                                  <button onClick={() => { setEditingItem({ ...item, aisle_id: aisle.id }); setShowAddItem(false); }} className="text-blue-600 hover:underline">Edit</button>
                                  <button onClick={() => handleDeleteItem(item.id)} className="text-red-500 hover:underline">Delete</button>
                                </div>
                              </div>
                            )}
                          </li>
                        ))
                      )}
                    </ul>
                  </div>

                  {/* Export */}
                  <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Export Layout</h3>
                    <button onClick={handleExport} className="w-full bg-gray-100 text-gray-700 text-sm py-2 rounded-lg hover:bg-gray-200 transition-colors">Download JSON</button>
                  </div>

                  {/* Import */}
                  <div className="bg-white border border-gray-200 rounded-xl p-4 shadow-sm">
                    <h3 className="text-sm font-semibold text-gray-700 mb-2">Import Layout</h3>
                    <textarea value={importJson} onChange={(e) => setImportJson(e.target.value)} rows={4} placeholder='Paste JSON layout here…' className="w-full border border-gray-300 rounded-lg px-3 py-2 text-xs font-mono focus:outline-none focus:ring-2 focus:ring-green-500 resize-none" />
                    <button onClick={handleImport} className="mt-2 w-full bg-green-700 text-white text-sm py-2 rounded-lg hover:bg-green-800 transition-colors">Import</button>
                    {importMsg && <p className="text-xs text-green-700 mt-2">{importMsg}</p>}
                  </div>
                </>
              )}
            </div>

            {/* Map */}
            <div className="flex-1 flex flex-col items-center justify-start pt-2">
              {!store && !storeLoading && (
                <div className="text-center text-gray-400 mt-20">
                  <div className="text-5xl mb-4">🏪</div>
                  <p className="text-lg font-medium">Load a store to edit its layout</p>
                </div>
              )}
              {storeLoading && <p className="text-gray-500 mt-20">Loading store…</p>}
              {store && (
                <div className="flex flex-col items-center gap-3">
                  <h3 className="text-lg font-semibold text-gray-700">{store.name}</h3>
                  <StoreMap
                    store={store}
                    onMapClick={handleMapClick}
                    editorMode={true}
                    onItemMoved={handleItemMoved}
                    onAisleMoved={handleAisleMoved}
                  />
                  <p className="text-xs text-gray-400">Drag aisles or items to reposition · Click empty space to place a new item</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* ======== OUT-OF-STOCK ======== */}
        {tab === 'Out-of-Stock' && (
          <div className="max-w-xl">
            <h2 className="text-lg font-semibold text-gray-800 mb-4">Out-of-Stock Report</h2>
            <div className="flex gap-2 mb-4">
              <input type="number" min={1} value={oosStoreIdInput} onChange={(e) => setOosStoreIdInput(e.target.value)} placeholder="Store ID" className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
              <button onClick={() => loadOos(oosStoreIdInput)} disabled={oosLoading} className="bg-green-700 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-800 transition-colors disabled:opacity-50">Load Report</button>
            </div>
            {oosError && <p className="text-red-500 text-sm mb-3">{oosError}</p>}
            {oosLoading && <p className="text-gray-500">Loading…</p>}
            {!oosLoading && oosStoreId && oosItems.length === 0 && (
              <p className="text-gray-500 text-sm">No out-of-stock items reported for this store.</p>
            )}
            {oosItems.length > 0 && (
              <table className="w-full bg-white border border-gray-200 rounded-xl overflow-hidden text-sm shadow-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="px-4 py-2 text-left">ID</th>
                    <th className="px-4 py-2 text-left">Item</th>
                    <th className="px-4 py-2 text-left">Position</th>
                    <th className="px-4 py-2 text-left">Aisle</th>
                  </tr>
                </thead>
                <tbody>
                  {oosItems.map((item) => (
                    <tr key={item.id} className="border-t border-gray-100 hover:bg-gray-50">
                      <td className="px-4 py-2 text-gray-400">{item.id}</td>
                      <td className="px-4 py-2 font-medium text-gray-800">{item.name}</td>
                      <td className="px-4 py-2 text-gray-500">({item.pos_x}, {item.pos_y})</td>
                      <td className="px-4 py-2 text-gray-500">{item.aisle_id}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
