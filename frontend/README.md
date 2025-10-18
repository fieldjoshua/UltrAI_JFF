# UltrAI Frontend

React-based web interface for the UltrAI Multi-LLM Synthesis Platform.

## Setup Instructions

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server:**
   ```bash
   npm run dev
   ```

3. **Build for production:**
   ```bash
   npm run build
   ```

## Project Structure

```
frontend/
├── src/
│   ├── components/     # React components
│   ├── services/       # API integration
│   ├── hooks/          # Custom React hooks
│   ├── animations/     # Animation configurations
│   └── shaders/        # Three.js shaders
├── public/             # Static assets
└── dist/               # Build output
```

## Tech Stack

- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Framer Motion** - Animations (PR 23)
- **Three.js** - 3D graphics (PR 24)

## Development Phases

- **PR 20** ✅ Frontend Foundation (React + Vite + Tailwind)
- **PR 21** 🔄 API Integration Layer
- **PR 22** 🔄 Core UI Components
- **PR 23** 🔄 Animation Layer (Framer Motion)
- **PR 24** 🔄 3D Interactive Background (Three.js)
- **PR 25** 🔄 Render Static Site Deployment

## API Integration

The frontend connects to the UltrAI FastAPI backend running on `localhost:8000`.

**Endpoints:**
- `POST /runs` - Start a new run
- `GET /runs/{run_id}/status` - Poll run status
- `GET /runs/{run_id}/artifacts` - Get run artifacts

## Testing

All tests use real API calls (no mocks) to ensure integration works correctly.

```bash
npm test
```
