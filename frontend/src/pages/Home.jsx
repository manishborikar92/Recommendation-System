// src/pages/Home.jsx
import React from "react";

const Home = () => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-3xl font-bold mb-6">Welcome to the Recommendation System</h1>
      <p className="text-gray-700">Explore personalized recommendations and trending items.</p>
      <a href="/register" className="text-blue-500">
            Register here
      </a>
    </div>
  );
};

export default Home;