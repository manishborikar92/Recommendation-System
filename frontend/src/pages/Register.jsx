// src/pages/Register.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/api';
import FormInput from '../components/FormInput';

const Register = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    otp: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleInitRegistration = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      await authService.registerInit({ name: formData.name, email: formData.email });
      setStep(2);
    } catch (error) {
      setErrors({
        general: error.response?.data?.error || 'An error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyRegistration = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      await authService.registerVerify({
        email: formData.email,
        password: formData.password,
        confirmPassword: formData.confirmPassword,
        otp: formData.otp
      });
      window.location.href = '/login?registered=true';
    } catch (error) {
      setErrors({
        general: error.response?.data?.error || 'An error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-lg">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        {step === 1 ? (
          <form className="mt-8 space-y-6" onSubmit={handleInitRegistration}>
            {errors.general && (
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-sm text-red-500">{errors.general}</p>
              </div>
            )}
            <FormInput
              label="Full Name"
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              error={errors.name}
            />
            <FormInput
              label="Email address"
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              error={errors.email}
            />
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? 'Sending OTP...' : 'Continue'}
            </button>
          </form>
        ) : (
          <form className="mt-8 space-y-6" onSubmit={handleVerifyRegistration}>
            {errors.general && (
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-sm text-red-500">{errors.general}</p>
              </div>
            )}
            <FormInput
              label="OTP"
              type="text"
              required
              value={formData.otp}
              onChange={(e) => setFormData({ ...formData, otp: e.target.value })}
              error={errors.otp}
              maxLength={6}
            />
            <FormInput
              label="Password"
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              error={errors.password}
            />
            <FormInput
              label="Confirm Password"
              type="password"
              required
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              error={errors.confirmPassword}
            />
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>
        )}
        <div className="text-center">
          <Link
            to="/login"
            className="text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Already have an account? Sign in
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;