import { useState } from 'react';

export default function ItemEditor({ aisles, onSave, onCancel, initial = {}, clickedPos = null }) {
  const [name, setName] = useState(initial.name ?? '');
  const [aisleId, setAisleId] = useState(initial.aisle_id ?? aisles[0]?.id ?? '');
  const [posX, setPosX] = useState(initial.pos_x ?? clickedPos?.[0]?.toFixed(2) ?? '');
  const [posY, setPosY] = useState(initial.pos_y ?? clickedPos?.[1]?.toFixed(2) ?? '');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ name, aisle_id: Number(aisleId), pos_x: Number(posX), pos_y: Number(posY) });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 bg-gray-50 border border-gray-200 rounded-xl p-4">
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Item Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="e.g. Organic Apples"
        />
      </div>
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Aisle</label>
        <select
          value={aisleId}
          onChange={(e) => setAisleId(e.target.value)}
          required
          className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
        >
          {aisles.map((a) => (
            <option key={a.id} value={a.id}>{a.name}</option>
          ))}
        </select>
      </div>
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">X position</label>
          <input type="number" step="0.1" value={posX} onChange={(e) => setPosX(e.target.value)} required className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
        </div>
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Y position</label>
          <input type="number" step="0.1" value={posY} onChange={(e) => setPosY(e.target.value)} required className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
        </div>
      </div>
      {clickedPos && <p className="text-xs text-green-700">Position set from map click</p>}
      <div className="flex gap-2 justify-end">
        {onCancel && <button type="button" onClick={onCancel} className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1.5">Cancel</button>}
        <button type="submit" className="bg-green-700 text-white text-sm px-4 py-1.5 rounded-lg hover:bg-green-800 transition-colors">Save Item</button>
      </div>
    </form>
  );
}
