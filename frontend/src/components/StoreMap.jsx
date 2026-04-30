import { useState, useRef } from 'react';

const SVG_SIZE = 560;
const PADDING = 20;

function getScale(store) {
  const w = store.width || 1;
  const h = store.height || 1;
  const available = SVG_SIZE - PADDING * 2;
  return Math.min(available / w, available / h);
}

const AISLE_COLORS = [
  '#bbf7d0', '#bfdbfe', '#fde68a', '#fecaca', '#ddd6fe',
  '#fbcfe8', '#fed7aa', '#a7f3d0', '#e9d5ff', '#bae6fd',
];

export default function StoreMap({
  store,
  routePath = null,
  highlightedItems = [],
  onMapClick = null,
  optimizedItems = [],
  editorMode = false,
  onItemMoved = null,
  onAisleMoved = null,
}) {
  const [dragging, setDragging] = useState(null);
  const [dragPos, setDragPos] = useState(null);
  const svgRef = useRef(null);
  const dragMoved = useRef(false);

  if (!store) return null;

  const scale = getScale(store);
  const toSvg = ([x, y]) => [PADDING + x * scale, PADDING + y * scale];
  const toStore = (svgX, svgY) => [(svgX - PADDING) / scale, (svgY - PADDING) / scale];
  const clamp = (val, min, max) => Math.max(min, Math.min(max, val));

  const getSvgPos = (e) => {
    const rect = svgRef.current.getBoundingClientRect();
    return [e.clientX - rect.left, e.clientY - rect.top];
  };

  const handleMouseDown = (e, type, element) => {
    if (!editorMode) return;
    e.stopPropagation();
    e.preventDefault();
    dragMoved.current = false;
    const [svgX, svgY] = getSvgPos(e);
    const [storeX, storeY] = toStore(svgX, svgY);
    setDragging({ type, element, startStoreX: storeX, startStoreY: storeY });
    if (type === 'item') {
      setDragPos({ x: element.pos_x ?? element.x, y: element.pos_y ?? element.y });
    } else {
      setDragPos({ x_min: element.x_min, y_min: element.y_min, x_max: element.x_max, y_max: element.y_max });
    }
  };

  const handleMouseMove = (e) => {
    if (!dragging || !dragPos) return;
    dragMoved.current = true;
    const [svgX, svgY] = getSvgPos(e);
    const [storeX, storeY] = toStore(svgX, svgY);
    const dx = storeX - dragging.startStoreX;
    const dy = storeY - dragging.startStoreY;

    if (dragging.type === 'item') {
      const el = dragging.element;
      setDragPos({
        x: clamp((el.pos_x ?? el.x) + dx, 0, store.width),
        y: clamp((el.pos_y ?? el.y) + dy, 0, store.height),
      });
    } else {
      const el = dragging.element;
      const w = el.x_max - el.x_min;
      const h = el.y_max - el.y_min;
      const newXMin = clamp(el.x_min + dx, 0, store.width - w);
      const newYMin = clamp(el.y_min + dy, 0, store.height - h);
      setDragPos({ x_min: newXMin, y_min: newYMin, x_max: newXMin + w, y_max: newYMin + h });
    }
  };

  const handleMouseUp = () => {
    if (!dragging || !dragPos) return;
    if (dragMoved.current) {
      if (dragging.type === 'item' && onItemMoved) {
        onItemMoved(dragging.element.id, dragPos.x, dragPos.y);
      } else if (dragging.type === 'aisle' && onAisleMoved) {
        onAisleMoved(dragging.element.id, dragPos.x_min, dragPos.y_min, dragPos.x_max, dragPos.y_max);
      }
    }
    setDragging(null);
    setDragPos(null);
    setTimeout(() => { dragMoved.current = false; }, 0);
  };

  const isDraggingItem = (id) => dragging?.type === 'item' && dragging.element.id === id;
  const isDraggingAisle = (id) => dragging?.type === 'aisle' && dragging.element.id === id;

  return (
    <svg
      ref={svgRef}
      width={SVG_SIZE}
      height={SVG_SIZE}
      className="border border-gray-200 rounded-xl bg-white"
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onClick={onMapClick ? (e) => {
        if (dragMoved.current) return;
        const rect = e.currentTarget.getBoundingClientRect();
        const x = (e.clientX - rect.left - PADDING) / scale;
        const y = (e.clientY - rect.top - PADDING) / scale;
        if (x >= 0 && y >= 0 && x <= store.width && y <= store.height) {
          onMapClick(x, y);
        }
      } : undefined}
      style={{
        cursor: dragging ? 'grabbing' : onMapClick ? 'crosshair' : 'default',
        userSelect: 'none',
      }}
    >
      {/* Store boundary */}
      <rect
        x={PADDING} y={PADDING}
        width={store.width * scale} height={store.height * scale}
        fill="#f0fdf4" stroke="#15803d" strokeWidth={2} rx={4}
      />

      {/* Aisles */}
      {store.aisles?.map((aisle, i) => {
        const active = isDraggingAisle(aisle.id);
        const pos = active ? dragPos : { x_min: aisle.x_min, y_min: aisle.y_min, x_max: aisle.x_max, y_max: aisle.y_max };
        const [x1, y1] = toSvg([pos.x_min, pos.y_min]);
        const w = (pos.x_max - pos.x_min) * scale;
        const h = (pos.y_max - pos.y_min) * scale;
        return (
          <g
            key={aisle.id}
            onMouseDown={editorMode ? (e) => handleMouseDown(e, 'aisle', aisle) : undefined}
            style={{ cursor: editorMode ? (active ? 'grabbing' : 'grab') : 'default' }}
          >
            <rect
              x={x1} y={y1} width={w} height={h}
              fill={AISLE_COLORS[i % AISLE_COLORS.length]}
              stroke={active ? '#15803d' : '#6b7280'}
              strokeWidth={active ? 2.5 : 1}
              strokeDasharray={active ? '5 3' : undefined}
              rx={2} opacity={0.85}
            />
            <text x={x1 + w / 2} y={y1 + h / 2} textAnchor="middle" dominantBaseline="middle" fontSize={10} fill="#374151" fontWeight="500" style={{ pointerEvents: 'none' }}>
              {aisle.name}
            </text>
          </g>
        );
      })}

      {/* Route path */}
      {routePath && routePath.length > 1 && (
        <polyline
          points={routePath.map(([x, y]) => toSvg([x, y]).join(',')).join(' ')}
          fill="none" stroke="#dc2626" strokeWidth={2.5} strokeDasharray="6 3" opacity={0.85}
        />
      )}

      {/* Items */}
      {store.aisles?.flatMap((aisle) =>
        aisle.items?.map((item) => {
          const active = isDraggingItem(item.id);
          const posX = active ? dragPos.x : (item.x ?? item.pos_x);
          const posY = active ? dragPos.y : (item.y ?? item.pos_y);
          const [cx, cy] = toSvg([posX, posY]);
          const isHighlighted = highlightedItems.includes(item.name);
          const orderIndex = optimizedItems.findIndex((o) => o.id === item.id);
          return (
            <g
              key={item.id}
              onMouseDown={editorMode ? (e) => handleMouseDown(e, 'item', item) : undefined}
              style={{ cursor: editorMode ? (active ? 'grabbing' : 'grab') : 'default' }}
            >
              <circle
                cx={cx} cy={cy}
                r={active ? 10 : isHighlighted ? 9 : 6}
                fill={isHighlighted ? '#dc2626' : '#15803d'}
                stroke={active ? '#f59e0b' : 'white'}
                strokeWidth={active ? 3 : 2}
              />
              {orderIndex >= 0 && (
                <text x={cx} y={cy} textAnchor="middle" dominantBaseline="middle" fontSize={8} fill="white" fontWeight="bold" style={{ pointerEvents: 'none' }}>
                  {orderIndex + 1}
                </text>
              )}
              <title>{item.name}</title>
            </g>
          );
        })
      )}

      {/* Path entrance marker */}
      {routePath && routePath.length > 0 && (() => {
        const [sx, sy] = toSvg(routePath[0]);
        return (
          <g>
            <circle cx={sx} cy={sy} r={8} fill="#1d4ed8" stroke="white" strokeWidth={2} />
            <text x={sx} y={sy} textAnchor="middle" dominantBaseline="middle" fontSize={8} fill="white" fontWeight="bold">E</text>
          </g>
        );
      })()}
    </svg>
  );
}
