# OptiShop — 15-Minute Live Demo Script

**Tagline:** Indoor GPS for Grocery Stores — route optimization powered by A* pathfinding and TSP algorithms.

---

## Before You Start (Pre-Demo Checklist)

- [ ] Backend running: `uvicorn backend.main:app --reload` (port 8000)
- [ ] Frontend running: `npm run dev` inside `frontend/` (port 5173)
- [ ] Browser open at `http://localhost:5173`
- [ ] Have two browser tabs ready (one for Shopper, one for Store Owner)
- [ ] A store already seeded in the database (or ready to create one live)
- [ ] Know the store ID (e.g., `1`) to type in the shopper view

---

## Segment 1 — Problem & Architecture Overview (1–2 min)

**Say:** "Have you ever walked into a grocery store with a list and zigzagged back and forth across every aisle? OptiShop solves that. It's an indoor navigation platform that computes the *shortest possible walking route* through a store based on your shopping list."

**Show** the project folder briefly in the editor:
- Point out `backend/` (Python FastAPI) and `frontend/` (React + Vite)
- Mention the two user roles: **Shopper** and **Store Owner**

---

## Segment 2 — Store Owner: Building a Store (4 min)

### 2a. Register as a Store Owner (30 sec)

1. Navigate to `/register`
2. Fill in email, password, select **Store Owner**
3. Click Register → redirected to the **Store Owner Dashboard**

**Say:** "Store owners configure the store layout once so every shopper benefits."

---

### 2b. Create a New Store (30 sec)

1. On the **Dashboard**, go to the **"Create Store"** tab
2. Enter a store name (e.g., `Campus Grocery`) and dimensions (e.g., `50 × 40`)
3. Click **Create Store**
4. Note the Store ID shown — shoppers will use this to load the store

---

### 2c. Design the Layout in the Visual Editor (2 min)

1. Switch to the **"Layout Editor"** tab
2. **Add an aisle:**
   - Click "Add Aisle", enter name (e.g., `Produce`), draw a bounding box by entering coordinates
   - The aisle appears as a rectangle on the SVG map
3. **Add items to the aisle:**
   - Select the aisle, click "Add Item", enter name (e.g., `Apples`) and click a position on the map
   - Repeat for a few more items across 2–3 aisles (e.g., `Milk`, `Bread`, `Eggs`, `Bananas`)
4. **Show editing:** click an existing item, drag it to a new position, or rename it

**Say:** "Every item gets precise (x, y) coordinates. These feed directly into the pathfinding algorithm."

---

### 2d. Export / Import (30 sec)

1. Click **Export Layout** — a JSON file downloads (or is shown)
2. Briefly show the JSON structure: store dimensions, aisles, item coordinates
3. Mention: "Chains can share a single layout file across locations."

---

## Segment 3 — Shopper: Optimized Route in Action (5 min)

### 3a. Register / Login as a Shopper (30 sec)

1. Open a new tab (or log out), go to `/register`
2. Register with a different email, select **Shopper**
3. Log in → redirected to the **Shopper View** (`/shop`)

---

### 3b. Load the Store (30 sec)

1. Type the Store ID from Segment 2 into the store selector
2. Click **Load Store**
3. The SVG map renders — aisles appear as grey blocks, items as colored dots

**Say:** "The map is built dynamically from the store layout. No hardcoded graphics."

---

### 3c. Build a Shopping List (1 min)

1. Click into the item search box
2. Start typing `Mi` — autocomplete suggests `Milk` from the store inventory
3. Add `Milk`, `Eggs`, `Bread`, `Bananas` (items from different aisles)
4. The selected items highlight in **red** on the map

**Say:** "The autocomplete only shows items that actually exist in this store."

---

### 3d. Optimize the Route (2 min)

1. Click **Optimize Route**
2. A dashed red path appears on the map connecting all selected items in order
3. The sidebar shows:
   - Items listed in the optimal walking order
   - Total estimated distance / steps

**Say:** "This is A* pathfinding combined with a TSP solver. For small lists (≤15 items) we use exact dynamic programming with bitmask — guaranteed optimal. For larger lists we switch to a nearest-neighbor heuristic so it stays fast."

**Point out on the map:**
- Entrance/exit markers (blue dots)
- The path routing *around* aisles, not through them (A* avoids obstacles)
- Order of stops reflects the shortest loop, not the order items were typed

---

### 3e. Save as a Favorite Cart (30 sec)

1. Click **Save Cart**, give it a name (e.g., `Weekly Run`)
2. Click **Favorites** — the saved cart appears
3. Click the cart to reload the list instantly

**Say:** "Shoppers can keep their regular lists and replay the optimized route any week."

---

## Segment 4 — Inventory & Out-of-Stock Reporting (2 min)

### 4a. Shopper Reports an Item (1 min)

1. Still in the Shopper View, find `Eggs` on the item list
2. Click **Report Out of Stock** next to it
3. A confirmation shows

**Say:** "Shoppers contribute real-time inventory signals back to the store."

---

### 4b. Store Owner Sees the Report (1 min)

1. Switch back to the Store Owner tab
2. Go to **Dashboard → "Out of Stock Reports"** tab
3. The `Eggs` report appears with a timestamp

**Say:** "Store staff can act on this immediately — no manual walkthrough needed."

---

## Segment 5 — Code Walkthrough: The Algorithm (2 min)

Open [backend/logic/routing_engine.py](backend/logic/routing_engine.py) and [backend/logic/strategies/tsp_exact.py](backend/logic/strategies/tsp_exact.py).

**Say and point to:**

1. `routing_engine.py` — `optimize_route()` method:
   - Builds the graph from store layout
   - Runs pairwise A* between all items to build a distance matrix
   - Dispatches to TSP strategy based on item count

2. `tsp_exact.py` — the DP loop:
   - `dp[mask][last]` = minimum cost to visit all items in `mask`, ending at `last`
   - Bitmask over items; only 2^n × n² states
   - Guarantees the shortest possible walk through all items

3. `nearest_neighbor.py` (brief) — fallback for large carts, O(n²) greedy

**Say:** "The algorithm is completely decoupled from the API. We can swap strategies without touching routes."

---

## Segment 6 — Tests (1 min)

Run in terminal:
```
pytest tests/ -v --tb=short
```

Point out:
- 44 tests — security, algorithm correctness, API integration
- Tests use in-memory SQLite so no real database needed
- Show a TSP test: exact answer verified against known optimal for a 4-item layout

**Say:** "Every core path is covered. The TSP exact solver is validated against hand-calculated optimal routes."

---

## Closing (30 sec)

**Summarize:**
- Store owners design layouts once using a visual editor
- Shoppers get an optimal route in one click, in real time
- Backend uses industry-standard algorithms (A*, TSP-DP) served via a clean REST API
- Full JWT auth, role separation, and a test suite backing every layer

**Possible questions to anticipate:**
- *"How does it handle large stores?"* → Nearest-neighbor heuristic kicks in above 15 items; grid resolution is configurable
- *"Does it work with real store data?"* → Import/export JSON allows any store to upload their layout
- *"What's the database?"* → Oracle 19c in production; SQLite in tests via SQLAlchemy abstraction

---

## Timing Summary

| Segment | Topic | Time |
|---------|-------|------|
| 1 | Problem + architecture overview | 1–2 min |
| 2 | Store Owner: create store + layout editor + export | 4 min |
| 3 | Shopper: load store, build list, optimize route, save cart | 5 min |
| 4 | Out-of-stock reporting (shopper → owner) | 2 min |
| 5 | Code walkthrough: A* + TSP algorithm | 2 min |
| 6 | Test suite | 1 min |
| — | Closing summary | 30 sec |
| **Total** | | **~15 min** |
