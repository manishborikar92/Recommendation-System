// src/pages/Login.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authService } from '../services/api';
import FormInput from '../components/FormInput';
import { ShoppingCart, Eye, EyeOff } from 'lucide-react';

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      const response = await authService.login(formData);
      login(response.data, response.data.token);
    } catch (error) {
      setErrors({
        general: error.response?.data?.error || 'An error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <div className="min-h-screen relative bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500">
      <div className="absolute inset-0 bg-black opacity-20"></div>
      
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -inset-[10px] opacity-50">
          <div className="absolute inset-0 rotate-45 transform scale-150 bg-gradient-to-r from-transparent via-white to-transparent blur-3xl animate-pulse"></div>
        </div>
      </div>

      <div className="relative min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 bg-white bg-opacity-95 p-8 rounded-2xl shadow-2xl transform transition-all duration-500 hover:scale-[1.02] hover:animate-blur-fade ease-in-out">
          <div className="text-center">
            <div className="flex justify-center mb-6">
              <ShoppingCart className="h-12 w-12 text-blue-600 animate-bounce" />
            </div>
            <h1 className="text-4xl font-extrabold text-gray-900 font-['Poppins']">
              Welcome !
            </h1>
            <h2 className="mt-2 text-xl text-gray-600">
              Sign in to discover personalized recommendations
            </h2>
          </div>

          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            {errors.general && (
              <div className="bg-red-50 p-4 rounded-lg transform transition-all duration-300 animate-shake">
                <p className="text-sm text-red-500">{errors.general}</p>
              </div>
            )}

            <div className="space-y-8">
              <FormInput
                label="Email address"
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                error={errors.email}
                className="transform transition-all duration-300 focus:scale-[1.02]"
              />
              <div className="relative">
                <FormInput
                  label="Password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  error={errors.password}
                  className="transform transition-all duration-300 focus:scale-[1.02]"
                />
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute right-3 top-9 text-gray-500 hover:text-gray-700 focus:outline-none"
                >
                  {showPassword ? (
                    <Eye className="h-5 w-5" />
                  ) : (
                    <EyeOff className="h-5 w-5" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-xl shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transform transition-all duration-300 hover:scale-[1.02] ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? (
                <span className="flex items-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Signing in...
                </span>
              ) : (
                'Sign in'
              )}
            </button>

            <div className="flex items-center justify-between mt-4 space-x-4">
              <Link
                to="/register"
                className="flex-1 text-center py-2 px-4 border border-blue-600 rounded-lg text-sm font-medium text-blue-600 hover:bg-blue-50 transform transition-all duration-300 hover:scale-[1.02]"
              >
                Create account
              </Link>
              <Link
                to="/password-reset"
                className="flex-1 text-center py-2 px-4 border border-blue-600 rounded-lg text-sm font-medium text-blue-600 hover:bg-blue-50 transform transition-all duration-300 hover:scale-[1.02]"
              >
                Reset password
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;

