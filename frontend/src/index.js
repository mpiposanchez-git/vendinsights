// Frontend entrypoint: mount the root React component into `public/index.html`.
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
import './index.css';

// The `root` div is created in `frontend/public/index.html`.
const container = document.getElementById('root');
const root = createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
