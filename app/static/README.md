# AI Quote Generator - React Frontend

A beautiful, dark-themed React application with purple accents, animated background particles, and fluid cursor effects.

## Features

- Dark theme with purple gradient design
- Animated background with floating purple particles
- Responsive design with Tailwind CSS
- Single-page application

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm start
```

Runs the app in development mode at [http://localhost:3000](http://localhost:3000).

### Build

```bash
npm run build
```

Builds the app for production to the `build` folder.

## Technologies Used

- React 18
- Tailwind CSS
- React SplashCursor
- JavaScript (ES6+)

## Customization

The purple theme colors are defined in `tailwind.config.js`:
- `purple-primary`: #6b46c1
- `purple-secondary`: #553c9a
- `purple-accent`: #7c3aed
- `purple-light`: #8b5cf6

## API Integration

Update the API endpoint in `src/components/QuoteGenerator.js` to connect with your backend:

```javascript
const response = await fetch('/api/quotes/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ topic: topic || 'inspiration' }),
});
```


---

<div align="center">
  <em>Built by AyaNexus 🦢</em>
</div>