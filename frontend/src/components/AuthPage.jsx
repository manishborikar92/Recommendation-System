import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AlertCircle, Mail, Lock, User, ArrowRight, Loader2 } from 'lucide-react';
import { authService } from '../services/authService';

const AuthPage = ({ mode = 'login' }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    token: ''
  });

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');

    try {
      let response;

      switch (mode) {
        case 'login':
          response = await authService.login({
            email: formData.email,
            password: formData.password
          });
          if (response.token && response.userId) {
            localStorage.setItem('userId', response.userId);
            localStorage.setItem('username', response.username);
            localStorage.setItem('token', response.token);
            navigate('/');
          }
          break;

        case 'register':
          response = await authService.register({
            email: formData.email,
            password: formData.password,
            username: formData.username
          });
          if (response.token && response.userId) {
            localStorage.setItem('userId', response.userId);
            localStorage.setItem('username', response.username);
            localStorage.setItem('token', response.token);
            navigate('/');
          }
          break;

        case 'forgot':
          response = await authService.forgotPassword(formData.email);
          setSuccess('Reset instructions sent to your email');
          setTimeout(() => navigate('/reset-password'), 3000);
          break;

        case 'reset':
          response = await authService.resetPassword(formData.token, formData.password);
          setSuccess('Password successfully reset');
          setTimeout(() => navigate('/login'), 3000);
          break;
      }
    } catch (err) {
      setError(err.message || 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="w-full max-w-md space-y-8 bg-white p-8 rounded-lg shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-bold tracking-tight text-gray-900">
            {mode === 'login' ? 'Sign in to your account' :
             mode === 'register' ? 'Create a new account' :
             mode === 'forgot' ? 'Forgot Password' : 'Reset Password'}
          </h2>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative" role="alert">
            <span className="block sm:inline flex items-center gap-2">
              <AlertCircle className="h-5 w-5" />
              {error}
            </span>
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded relative">
            {success}
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {mode !== 'reset' && (
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email address
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="you@example.com"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
            </div>
          )}

          {mode === 'register' && (
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  name="username"
                  type="text"
                  required
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="johndoe"
                  value={formData.username}
                  onChange={handleChange}
                />
              </div>
            </div>
          )}

          {mode !== 'forgot' && (
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  name="password"
                  type="password"
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                  required
                  className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                  minLength={6}
                />
              </div>
            </div>
          )}

          {mode === 'reset' && (
            <div>
              <label htmlFor="token" className="block text-sm font-medium text-gray-700">
                Reset Token
              </label>
              <input
                id="token"
                name="token"
                type="text"
                required
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                value={formData.token}
                onChange={handleChange}
              />
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="h-5 w-5 animate-spin" />
              ) : (
                <>
                  <span className="absolute left-0 inset-y-0 flex items-center pl-3">
                    <Lock className="h-5 w-5 text-blue-500 group-hover:text-blue-400" />
                  </span>
                  {mode === 'login' ? 'Sign in' :
                   mode === 'register' ? 'Sign up' :
                   mode === 'forgot' ? 'Send reset instructions' : 'Reset password'}
                </>
              )}
            </button>
          </div>
        </form>

        <div className="mt-6 flex flex-col space-y-2">
          {mode === 'login' ? (
            <>
              <p className="text-center text-sm text-gray-600">
                Don't have an account?{' '}
                <a href="/register" className="font-medium text-blue-600 hover:text-blue-500">
                  Sign up
                </a>
              </p>
              <p className="text-center text-sm">
                <a href="/forgot-password" className="font-medium text-blue-600 hover:text-blue-500">
                  Forgot your password?
                </a>
              </p>
            </>
          ) : mode === 'register' ? (
            <p className="text-center text-sm text-gray-600">
              Already have an account?{' '}
              <a href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                Sign in
              </a>
            </p>
          ) : (
            <p className="text-center text-sm">
              <a href="/login" className="font-medium text-blue-600 hover:text-blue-500">
                Back to login
              </a>
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

export default AuthPage;