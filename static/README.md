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

## Notifications

`src/components/Toast.js` provides the toasts. The app is wrapped in `<ToastProvider>`;
any component can then call:

```javascript
const toast = useToast();
toast.success('Quote copied to clipboard.');
toast.error(message, { id: 'generate' }); // same id replaces instead of stacking
toast.warning(message, { dir: 'rtl' });   // Arabic text
toast.info(message, { duration: 0 });     // stays until dismissed
```

Errors and warnings are announced to screen readers immediately (`role="alert"`), the
others politely. Toasts pause while hovered or focused and close with their button or
Escape.

---

<div align="center">
  <em>Built by AyaNexus 🦢</em>
</div>