# AlphaSignal Frontend

React + TypeScript frontend for the AlphaSignal crude oil prediction system.

## Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

The app will run on http://localhost:3000

### 3. Build for Production
```bash
npm run build
```

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client
│   ├── components/    # Reusable components
│   ├── pages/         # Page components
│   ├── App.tsx        # Main app with routing
│   ├── main.tsx       # Entry point
│   └── index.css      # Global styles
├── index.html
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── vite.config.ts
```

## Features

- ✅ Responsive design (mobile-first)
- ✅ Dark mode support
- ✅ TypeScript for type safety
- ✅ Tailwind CSS for styling
- ✅ React Router for navigation
- ✅ Axios for API calls

## Pages

1. **Landing** - Hero section with project overview
2. **Dashboard** - Live predictions and charts
3. **Backtesting** - Historical performance validation
4. **RL Agent** - Reinforcement learning recommendations
5. **Methodology** - Technical documentation
6. **About** - Project information

## Environment Variables

Create a `.env` file:

```
VITE_API_URL=http://localhost:8000
```

## Development

The frontend connects to the FastAPI backend running on port 8000. Make sure the backend is running before starting the frontend.

## Deployment

Deploy to Vercel:
```bash
npm run build
vercel --prod
```
