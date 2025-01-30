// src/pages/PasswordReset.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/api';
import FormInput from '../components/FormInput';

const PasswordReset = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    email: '',
    otp: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleInitReset = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      await authService.resetInit({ email: formData.email });
      setStep(2);
    } catch (error) {
      setErrors({
        general: error.response?.data?.error || 'An error occurred'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleVerifyReset = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    try {
      await authService.resetVerify({
        email: formData.email,
        otp: formData.otp,
        password: formData.password,
        confirmPassword: formData.confirmPassword
      });
      window.location.href = '/login?reset=success';
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
            {step === 1 ? 'Reset Your Password' : 'Verify OTP & Set New Password'}
          </h2>
        </div>
        {step === 1 ? (
          <form className="mt-8 space-y-6" onSubmit={handleInitReset}>
            {errors.general && (
              <div className="bg-red-50 p-4 rounded-lg">
                <p className="text-sm text-red-500">{errors.general}</p>
              </div>
            )}
            <FormInput
              label="Email address"
              type="email"
              required
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              error={errors.email}
              placeholder="Enter your registered email"
            />
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? 'Sending OTP...' : 'Send Reset OTP'}
            </button>
          </form>
        ) : (
          <form className="mt-8 space-y-6" onSubmit={handleVerifyReset}>
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
              placeholder="Enter 6-digit OTP"
            />
            <FormInput
              label="New Password"
              type="password"
              required
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              error={errors.password}
              placeholder="Enter new password"
            />
            <FormInput
              label="Confirm New Password"
              type="password"
              required
              value={formData.confirmPassword}
              onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
              error={errors.confirmPassword}
              placeholder="Confirm new password"
            />
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? 'Resetting Password...' : 'Reset Password'}
            </button>
          </form>
        )}
        <div className="flex items-center justify-center space-x-4">
          <Link
            to="/login"
            className="text-sm font-medium text-blue-600 hover:text-blue-500"
          >
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PasswordReset;