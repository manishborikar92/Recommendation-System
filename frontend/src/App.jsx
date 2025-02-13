// src/App.jsx
import React from 'react';
 import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
 import PrivateRoute from './components/PrivateRoute';
 import HomePage from './pages/HomePage';
 import ProductPage from './pages/ProductPage';
 import SearchPage from './pages/SearchPage';
 import Login from './pages/Login';
 import Register from './pages/Register';
 import PasswordReset from './pages/PasswordReset';
 import ErrorBoundary from './components/ErrorBoundary';
 import Navbar from './components/Navbar';

 const App = () => {
     const location = useLocation();
     const showNavbar =
       location.pathname === "/" ||
       location.pathname.startsWith("/product") ||
       location.pathname.startsWith("/search");
   
     return (
       <ErrorBoundary>
         <div className="min-h-screen bg-gray-50">
           {showNavbar && <Navbar />}
           <Routes>
             <Route path="/" element={<HomePage />} />
             <Route path="/product/:id" element={<ProductPage />} />
             <Route path="/search" element={<SearchPage />} />
             <Route path="/login" element={<Login />} />
             <Route path="/register" element={<Register />} />
             <Route path="/password-reset" element={<PasswordReset />} />
             <Route path="*" element={<Navigate to="/" replace />} />
           </Routes>
         </div>
       </ErrorBoundary>
     );
   };
   
   export default App;