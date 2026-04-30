import { useState } from 'react';

export default function ShoppingList({ items, onChange, storeItems = [] }) {
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState([]);

  const handleInput = (val) => {
    setInput(val);
    if (val.length > 0) {
      setSuggestions(
        storeItems
          .filter((s) => s.toLowerCase().includes(val.toLowerCase()) && !items.includes(s))
          .slice(0, 6)
      );
    } else {
      setSuggestions([]);
    }
  };

  const add = (name) => {
    const trimmed = name.trim();
    if (trimmed && !items.includes(trimmed)) {
      onChange([...items, trimmed]);
    }
    setInput('');
    setSuggestions([]);
  };

  const remove = (name) => onChange(items.filter((i) => i !== name));

  return (
    <div className="flex flex-col gap-3">
      <div className="relative">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => handleInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') { e.preventDefault(); add(input); }
            }}
            placeholder="Type item name…"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <button
            onClick={() => add(input)}
            className="bg-green-700 text-white px-3 py-2 rounded-lg text-sm hover:bg-green-800 transition-colors"
          >
            Add
          </button>
        </div>
        {suggestions.length > 0 && (
          <ul className="absolute z-10 top-full mt-1 w-full bg-white border border-gray-200 rounded-lg shadow-lg overflow-hidden">
            {suggestions.map((s) => (
              <li
                key={s}
                onClick={() => add(s)}
                className="px-3 py-2 text-sm hover:bg-green-50 cursor-pointer"
              >
                {s}
              </li>
            ))}
          </ul>
        )}
      </div>

      {items.length === 0 && (
        <p className="text-sm text-gray-400 italic">No items added yet</p>
      )}

      <ul className="flex flex-col gap-1">
        {items.map((item, i) => (
          <li key={item} className="flex items-center justify-between bg-gray-50 border border-gray-200 rounded-lg px-3 py-2 text-sm">
            <span className="text-gray-700">{i + 1}. {item}</span>
            <button onClick={() => remove(item)} className="text-gray-400 hover:text-red-500 transition-colors text-xs">✕</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
