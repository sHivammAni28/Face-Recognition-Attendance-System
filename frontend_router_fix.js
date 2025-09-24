// Add this to your main App.js or router setup file

import { BrowserRouter } from 'react-router-dom';

// Replace your current BrowserRouter with:
<BrowserRouter
  future={{
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  }}
>
  {/* Your app content */}
</BrowserRouter>

// OR if using createBrowserRouter:
import { createBrowserRouter } from 'react-router-dom';

const router = createBrowserRouter(routes, {
  future: {
    v7_startTransition: true,
    v7_relativeSplatPath: true,
  },
});