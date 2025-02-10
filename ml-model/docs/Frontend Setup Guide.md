# Frontend Setup Guide: React, Vite & Tailwind CSS

This guide will walk you through setting up a modern React frontend using Vite and Tailwind CSS. It also includes instructions for integrating with the backend recommendation system (endpoints such as `/api/v1/recommendations/home`).

---

## 1. Prerequisites

- [Node.js](https://nodejs.org/) (version 14+ recommended)
- [npm](https://www.npmjs.com/) or [Yarn](https://yarnpkg.com/)

---

## 2. Create a New React Project Using Vite

Open your terminal and run the following commands:

```bash
# Create a new Vite project using the React template
npm create vite@latest my-frontend -- --template react

# Change directory into the project folder
cd my-frontend

# Install dependencies
npm install
```

---

## 3. Install Tailwind CSS

Follow these steps to add Tailwind CSS to your Vite project.

### 3.1. Install Tailwind and its Dependencies

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 3.2. Configure Tailwind

Replace the content of your `tailwind.config.js` file with:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### 3.3. Add Tailwind Directives

Open `src/index.css` (or create it if it doesn't exist) and add the following:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Make sure to import this CSS file in your `src/main.jsx` or `src/index.jsx`:

```javascript
// src/main.jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css'; // Import Tailwind CSS

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

---

## 4. Create a Basic UI for Recommendations

Below is an example of how to create a simple page in React that calls the backend `/home` endpoint and displays the recommendations.

### 4.1. Create a New Component

Create a file `src/components/HomeRecommendations.jsx`:

```jsx
// src/components/HomeRecommendations.jsx
import React, { useState, useEffect } from 'react';

const HomeRecommendations = () => {
  const [loading, setLoading] = useState(true);
  const [recommendations, setRecommendations] = useState(null);
  const [error, setError] = useState(null);

  // Adjust the user_id as needed.
  const user_id = "testUser123";

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/recommendations/home?user_id=${user_id}`);
        if (!response.ok) {
          throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();
        setRecommendations(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [user_id]);

  if (loading) return <div className="text-center mt-10 text-xl">Loading recommendations...</div>;
  if (error) return <div className="text-center mt-10 text-red-500">Error: {error}</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Home Recommendations</h1>
      
      {/* Trending Products */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Trending</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {recommendations.trending.map((product) => (
            <div key={product.id} className="bg-white p-4 rounded shadow">
              <img src={product.image} alt={product.name} className="w-full h-32 object-cover mb-2" />
              <h3 className="font-semibold">{product.name}</h3>
              <p className="text-sm text-gray-500">{product.category}</p>
              <p className="font-bold text-green-600">${product.price}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Personalized Recommendations (if any) */}
      {recommendations.personalized.length > 0 && (
        <section className="mb-8">
          <h2 className="text-xl font-semibold mb-2">Personalized for You</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {recommendations.personalized.map((product) => (
              <div key={product.id} className="bg-white p-4 rounded shadow">
                <img src={product.image} alt={product.name} className="w-full h-32 object-cover mb-2" />
                <h3 className="font-semibold">{product.name}</h3>
                <p className="text-sm text-gray-500">{product.category}</p>
                <p className="font-bold text-green-600">${product.price}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Best Value, Top Categories, and Diverse Picks sections can be added similarly */}
    </div>
  );
};

export default HomeRecommendations;
```

### 4.2. Update Your Main App Component

Edit `src/App.jsx` to render the new component:

```jsx
// src/App.jsx
import React from 'react';
import HomeRecommendations from './components/HomeRecommendations';

function App() {
  return (
    <div className="min-h-screen bg-gray-100">
      <HomeRecommendations />
    </div>
  );
}

export default App;
```

---

## 5. Run Your Frontend

Start the Vite development server:

```bash
npm run dev
```

Open your browser and visit [http://localhost:3000](http://localhost:3000) (or the URL printed in your terminal) to see your new frontend.

---

## 6. Further Considerations

- **API Base URL:**  
  In a production setting, consider managing your backend URL in an environment variable or a configuration file.

- **Error Handling:**  
  Enhance error handling and user feedback as needed.

- **Styling:**  
  Explore additional Tailwind CSS utilities/classes to improve the design and responsiveness of your UI.

- **Routing:**  
  Use React Router if your application requires multiple pages or deeper navigation.

- **State Management:**  
  For larger applications, consider integrating state management libraries (e.g., Redux, Zustand) as your project grows.

---

With these steps, you should have a basic React frontend using Vite and Tailwind CSS integrated with your recommendation system backend. Happy coding!