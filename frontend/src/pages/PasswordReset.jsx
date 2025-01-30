// src\pages\PasswordReset.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { authService } from '../services/api';
import FormInput from '../components/FormInput';
import { KeyRound, Eye, EyeOff } from 'lucide-react';

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
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword((prev) => !prev);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword((prev) => !prev);
  };

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

  const handleOtpChange = (e, index) => {
    const value = e.target.value;
    if (/^[0-9]$/.test(value) || value === '') {
      const otpArr = formData.otp.split('');
      otpArr[index] = value;
      setFormData({ ...formData, otp: otpArr.join('') });

      // Move focus to the next input if value is entered
      if (value && index < 5) {
        document.getElementById(`otp-${index + 1}`).focus();
      }
    }
  };

  const handleOtpKeyDown = (e, index) => {
    if (e.key === 'Backspace' && index > 0) {
      const otpArr = formData.otp.split('');
      otpArr[index] = '';
      setFormData({ ...formData, otp: otpArr.join('') });

      // Move focus to the previous input if backspace is pressed
      document.getElementById(`otp-${index - 1}`).focus();
    }
  };

  const handleOtpPaste = (e) => {
    e.preventDefault();
    const pastedValue = e.clipboardData.getData('Text');
    const otpArr = formData.otp.split('');

    if (pastedValue.length <= 6) {
      for (let i = 0; i < pastedValue.length; i++) {
        otpArr[i] = pastedValue[i];
      }
      setFormData({ ...formData, otp: otpArr.join('') });
    }

    // Focus the next input if all the pasted characters are filled
    const nextEmptyIndex = otpArr.findIndex((char) => char === '');
    if (nextEmptyIndex !== -1) {
      document.getElementById(`otp-${nextEmptyIndex}`).focus();
    }
  };

  return (
    <div className="min-h-screen relative bg-gradient-to-br from-green-500 via-teal-500 to-blue-500">
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
              <KeyRound className="h-12 w-12 text-teal-600 animate-bounce" />
            </div>
            <h2 className="text-4xl font-bold text-gray-900 font-['Poppins']">
              {step === 1 ? 'Reset Password' : 'Set New Password'}
            </h2>
            <p className="mt-2 text-gray-600">
              {step === 1 
                ? 'Enter your email to receive reset instructions' 
                : 'Enter the verification code and your new password'}
            </p>
          </div>
          {step === 1 ? (
            <form className="mt-8 space-y-8 mb-6" onSubmit={handleInitReset}>
              <FormInput
                label="Email address"
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                error={errors.email}
                placeholder="Enter your registered email"
              />
              <button type="submit" disabled={isLoading} className="w-full py-3 px-4 text-white bg-teal-600 hover:bg-teal-700 rounded-xl">
                {isLoading ? 'Sending OTP...' : 'Send Reset Code'}
              </button>
            </form>
          ) : (
            <form className="mt-8 space-y-6" onSubmit={handleVerifyReset}>
              <label className="mb-2 block text-sm font-medium text-gray-700">Enter Verification Code</label>
              <div className="otp-container flex justify-center space-x-5">
                {[...Array(6)].map((_, index) => (
                  <input
                    key={index}
                    type="text"
                    maxLength={1}
                    value={formData.otp[index] || ''}
                    onChange={(e) => handleOtpChange(e, index)}
                    onKeyDown={(e) => handleOtpKeyDown(e, index)}
                    onPaste={handleOtpPaste}
                    id={`otp-${index}`}
                    className="w-12 h-12 text-center text-lg font-semibold border-2 border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-teal-600"
                    placeholder="-"
                  />
                ))}
              </div>

              {/* New Password Field with Toggle */}
              <div className="relative">
                <FormInput
                  label="New Password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  error={errors.password}
                  placeholder="Enter new password"
                />
                <button
                  type="button"
                  onClick={togglePasswordVisibility}
                  className="absolute right-3 top-9 text-gray-500 hover:text-gray-700 focus:outline-none"
                >
                  {showPassword ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
                </button>
              </div>

              {/* Confirm New Password Field with Toggle */}
              <div className="relative">
                <FormInput
                  label="Confirm New Password"
                  type={showConfirmPassword ? 'text' : 'password'}
                  required
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  error={errors.confirmPassword}
                  placeholder="Confirm new password"
                />
                <button
                  type="button"
                  onClick={toggleConfirmPasswordVisibility}
                  className="absolute right-3 top-9 text-gray-500 hover:text-gray-700 focus:outline-none"
                >
                  {showConfirmPassword ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
                </button>
              </div>

              <button type="submit" disabled={isLoading} className="w-full py-3 px-4 text-white bg-teal-600 hover:bg-teal-700 rounded-xl">
                {isLoading ? 'Resetting Password...' : 'Reset Password'}
              </button>
            </form>
          )}
          <div className="flex items-center justify-center mt-6">
            <Link to="/login" className="text-teal-600 hover:text-teal-500">
              Back to Login
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PasswordReset;
