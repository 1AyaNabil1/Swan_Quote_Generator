import React from 'react';
import ReactDOM from 'react-dom/client';
import { installHostBridge, setMockLoader } from '@zibby-run/app-kit';
// Every face comes from the bundle: nothing may load from a CDN on Zibby.
import '@fontsource/amiri/400.css';
import '@fontsource/amiri/700.css';
import '@fontsource/cairo/300.css';
import '@fontsource/cairo/400.css';
import '@fontsource/cairo/500.css';
import '@fontsource/crimson-text/400.css';
import '@fontsource/crimson-text/400-italic.css';
import '@fontsource/crimson-text/600.css';
import '@fontsource/crimson-text/600-italic.css';
import '@fontsource/poppins/300.css';
import '@fontsource/poppins/400.css';
import '@fontsource/poppins/500.css';
import '@fontsource/poppins/600.css';
import './index.css';
import App from './App';

// The mock answers locally in `npm run dev`, with no network and no credits; it is
// not built into production.
if (import.meta.env.DEV) {
  setMockLoader(() => import('./lib/zibbyMock').then((m) => m.mockStream));
  if (window.__zibbyAiMock === undefined) window.__zibbyAiMock = true;
}
if (import.meta.env.DEV && window.parent === window) {
  import('@zibby-run/app-kit/mock').then((m) => m.installMockHostBridge());
} else {
  installHostBridge();
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
