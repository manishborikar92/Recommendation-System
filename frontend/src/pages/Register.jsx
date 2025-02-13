import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/api';
import FormInput from '../components/FormInput';
import OTPInput from '../components/OTPInput';

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

  // Add resend OTP handler
  const handleResendOTP = async () => {
    try {
      await authService.registerInit({ 
        name: formData.name, 
        email: formData.email 
      });
    } catch (error) {
      setErrors({
        general: error.response?.data?.error || 'Failed to resend OTP'
      });
    }
  };

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

  const handleOtpChange = (otp) => {
    setFormData(prev => ({ ...prev, otp }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-6 bg-white p-8 rounded-2xl shadow-xl border border-gray-100">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold text-gray-900">
            Create your account
          </h2>
          <div className="flex justify-center items-center space-x-2">
            <div className={`h-2 w-8 rounded-full ${step === 1 ? 'bg-blue-600' : 'bg-gray-300'}`} />
            <div className={`h-2 w-8 rounded-full ${step === 2 ? 'bg-blue-600' : 'bg-gray-300'}`} />
          </div>
        </div>
        
        {errors.general && (
          <div className="bg-red-50 p-4 rounded-lg flex items-center gap-2 text-red-700">
            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span className="text-sm">{errors.general}</span>
          </div>
        )}

        {step === 1 ? (
          <form className="space-y-4" onSubmit={handleInitRegistration}>
            <FormInput
              label="Full Name"
              type="text"
              placeholder="John Doe"
              required
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              error={errors.name}
            />
            <FormInput
              label="Email address"
              type="email"
              placeholder="john@example.com"
              required
              value={formData.email}
              onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
              error={errors.email}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-lg border border-transparent font-semibold bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <span className="animate-spin inline-block w-4 h-4 border-[3px] border-current border-t-transparent rounded-full" />
                  Sending OTP...
                </>
              ) : 'Continue'}
            </button>
          </form>
        ) : (
          <form className="space-y-4" onSubmit={handleVerifyRegistration}>
            <OTPInput
              value={formData.otp}
              onChange={handleOtpChange}
              error={errors.otp}
              onResend={handleResendOTP}
              resendable={!isLoading}
            />
            <FormInput
              label="Password"
              type="password"
              placeholder="••••••••"
              required
              value={formData.password}
              onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
              error={errors.password}
            />
            <FormInput
              label="Confirm Password"
              type="password"
              placeholder="••••••••"
              required
              value={formData.confirmPassword}
              onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
              error={errors.confirmPassword}
            />
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 px-4 inline-flex justify-center items-center gap-2 rounded-lg border border-transparent font-semibold bg-blue-600 text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <span className="animate-spin inline-block w-4 h-4 border-[3px] border-current border-t-transparent rounded-full" />
                  Creating Account...
                </>
              ) : 'Create Account'}
            </button>
          </form>
        )}
        
        <p className="text-center text-sm text-gray-600">
          Already have an account?{' '}
          <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-500 transition-colors">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
};

export default Register;