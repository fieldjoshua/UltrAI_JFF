# PR 20: Instructions for General-Purpose Agent (Builder)

## Your Role
You are the **Implementation Lead** for PR 20 (Frontend Foundation). Your job is to scaffold the React + Vite + Tailwind foundation so the native Cursor editor can test it.

---

## What You're Building

A minimal React application with:
- **Vite** as the build tool (fast dev server, optimized production builds)
- **Tailwind CSS** for styling (utility-first CSS framework)
- **Placeholder UI** showing "UltrAI Frontend" text (no functionality yet)

**NO BACKEND INTEGRATION YET** — That's PR 21. This is just the scaffold.

---

## Step-by-Step Instructions

### Step 1: Create frontend/ Directory Structure

Create these files in the `frontend/` directory:

```
frontend/
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
├── index.html
├── README.md
└── src/
    ├── main.jsx
    ├── App.jsx
    └── index.css
```

### Step 2: Write package.json

```json
{
  "name": "ultrai-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.1",
    "tailwindcss": "^3.4.17",
    "postcss": "^8.4.49",
    "autoprefixer": "^10.4.20"
  }
}
```

### Step 3: Write vite.config.js

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
```

### Step 4: Write tailwind.config.js

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### Step 5: Write postcss.config.js

```javascript
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

### Step 6: Write index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>UltrAI</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### Step 7: Write src/main.jsx

```javascript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

### Step 8: Write src/App.jsx

```javascript
function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-black text-white">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-5xl font-bold text-center mb-8">
          UltrAI Frontend
        </h1>
        <p className="text-center text-xl text-gray-300">
          Multi-LLM synthesis system foundation
        </p>
        <div className="mt-12 text-center">
          <p className="text-sm text-gray-400">
            React + Vite + Tailwind CSS scaffold
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
```

### Step 9: Write src/index.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
```

### Step 10: Write frontend/README.md

```markdown
# UltrAI Frontend

React-based web interface for the UltrAI multi-LLM synthesis system.

## Tech Stack

- **React 18.3** - UI framework
- **Vite 6.0** - Build tool and dev server
- **Tailwind CSS 3.4** - Utility-first styling

## Setup

```bash
cd frontend
npm install
```

## Development

Start the dev server:
```bash
npm run dev
```

Visit http://localhost:5173 in your browser.

## Production Build

Build for production:
```bash
npm run build
```

Preview production build:
```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── App.jsx          # Root component
│   ├── main.jsx         # React entry point
│   └── index.css        # Tailwind directives
├── index.html           # HTML template
├── vite.config.js       # Vite configuration
├── tailwind.config.js   # Tailwind configuration
└── package.json         # Dependencies
```

## Current Status

**PR 20 - Foundation**: Basic scaffold with placeholder UI ✅
**PR 21 - API Integration**: Coming next
```

---

## After You're Done

Hand off to **Native Cursor Editor** with this message:

```
✅ PR 20 implementation complete. Frontend scaffold ready for testing.

Created:
- frontend/package.json (React 18 + Vite 6 + Tailwind 3)
- frontend/vite.config.js (dev server on port 5173)
- frontend/src/App.jsx (placeholder UI with gradient background)
- All configuration files (Tailwind, PostCSS)
- frontend/README.md (setup instructions)

Next Step: Native Cursor Editor should run these tests:
1. cd frontend && npm install
2. npm run dev → verify http://localhost:5173 loads
3. Check UI shows "UltrAI Frontend" with purple/blue gradient
4. npm run build → verify dist/ directory created
5. npm run preview → verify production build works

If all tests pass, ready for user approval to merge PR 20.
```

---

## Important Notes

### ✅ DO:
- Create ALL files listed above
- Use exact file structure shown
- Include Tailwind utility classes in App.jsx (proves Tailwind works)
- Add gradient background (shows styling works)
- Keep it minimal (no extra components yet)

### ❌ DON'T:
- Add API integration (that's PR 21)
- Create QueryForm component (that's PR 22)
- Add animations (that's PR 23)
- Add Three.js (that's PR 24)
- Install extra packages not listed in package.json

---

## Verification Checklist

Before handing off, confirm:
- [ ] All 10 files created
- [ ] package.json has correct dependencies
- [ ] vite.config.js sets port 5173
- [ ] App.jsx uses Tailwind classes (bg-gradient-to-br, text-5xl, etc.)
- [ ] index.html includes script tag for main.jsx
- [ ] README.md has setup instructions

---

## Questions?

If you encounter issues:
1. Check that all files match the structure above
2. Verify package.json has exact versions shown
3. Make sure Tailwind directives in index.css (@tailwind base, etc.)
4. Confirm vite.config.js imports '@vitejs/plugin-react'

Hand off to native editor when all files created successfully.
