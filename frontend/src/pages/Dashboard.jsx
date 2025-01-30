// src/pages/Dashboard.jsx (Add a basic dashboard component)
import React from 'react';
import { useAuth } from '../context/AuthContext';

const Dashboard = () => {
  const { user, logout } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Logout
          </button>
        </div>
        <div className="space-y-4">
          <p className="text-gray-600">Welcome back, {user?.name}!</p>
          <p className="text-gray-600">Email: {user?.email}</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
