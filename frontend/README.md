# OptiShop Frontend

React + Vite SPA for the OptiShop indoor shopping route optimizer. Connects to the FastAPI backend running on `localhost:8000`.

## Prerequisites

- Node.js 18+
- The OptiShop backend running (`python -m backend.main` from the repo root)

## Install & Run

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

## Pages

### `/login` and `/register`
Create an account as either a **Shopper** or **Store Owner**, then sign in. JWT tokens are stored in `localStorage` and sent automatically with every API request.

### `/shop` — Shopper View
1. Enter a **Store ID** and click **Load** to fetch the store layout
2. The store map renders as an interactive SVG showing all aisles and items
3. Add items to your **Shopping List** (autocomplete from the store's inventory)
4. Click **Optimize Route** — the app calls the backend's A\*/TSP engine and draws the optimal walking path on the map
5. The sidebar shows the **ordered item list** and total estimated distance
6. Save your list as a **Favorite Cart** for later

### `/dashboard` — Store Owner Dashboard _(store_owner role only)_

| Tab | What you can do |
|-----|----------------|
| My Stores | Create new stores with a name and dimensions |
| Layout Editor | Load a store, add/edit/delete aisles and items. Click on the map to place items by coordinate. Export/import layouts as JSON. |
| Out-of-Stock | View items that have been reported out-of-stock by shoppers |

## Configuration

The API base URL is set in `src/api/client.js`:

```js
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});
```

Change this if your backend runs on a different host or port.

## Tech Stack

| | |
|---|---|
| Framework | React 18 + Vite |
| Routing | react-router-dom v6 |
| HTTP | axios |
| Styling | Tailwind CSS |
| Map rendering | SVG (no external library) |
