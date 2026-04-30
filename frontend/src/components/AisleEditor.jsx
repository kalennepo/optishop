import { useState } from 'react';

export default function AisleEditor({ onSave, onCancel, initial = {} }) {
  const [name, setName] = useState(initial.name ?? '');
  const [xMin, setXMin] = useState(initial.x_min ?? '');
  const [yMin, setYMin] = useState(initial.y_min ?? '');
  const [xMax, setXMax] = useState(initial.x_max ?? '');
  const [yMax, setYMax] = useState(initial.y_max ?? '');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({ name, x_min: Number(xMin), y_min: Number(yMin), x_max: Number(xMax), y_max: Number(yMax) });
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-3 bg-gray-50 border border-gray-200 rounded-xl p-4">
      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Aisle Name</label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          placeholder="e.g. Produce"
        />
      </div>
      <div className="grid grid-cols-2 gap-2">
        {[['x_min', xMin, setXMin], ['y_min', yMin, setYMin], ['x_max', xMax, setXMax], ['y_max', yMax, setYMax]].map(([label, val, set]) => (
          <div key={label}>
            <label className="block text-xs font-medium text-gray-600 mb-1">{label}</label>
            <input
              type="number"
              step="0.1"
              value={val}
              onChange={(e) => set(e.target.value)}
              required
              className="w-full border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        ))}
      </div>
      <div className="flex gap-2 justify-end">
        {onCancel && <button type="button" onClick={onCancel} className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1.5">Cancel</button>}
        <button type="submit" className="bg-green-700 text-white text-sm px-4 py-1.5 rounded-lg hover:bg-green-800 transition-colors">Save Aisle</button>
      </div>
    </form>
  );
}
