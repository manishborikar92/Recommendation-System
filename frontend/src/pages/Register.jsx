// src/pages/Register.jsx
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Eye, EyeOff } from 'lucide-react';

const Register = () => {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    otp: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  const toggleConfirmPasswordVisibility = () => {
    setShowConfirmPassword(!showConfirmPassword);
  };

  const handleInitRegistration = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setStep(2);
    }, 1500);
  };

  const handleVerifyRegistration = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      window.location.href = '/login?registered=true';
    }, 1500);
  };

  const handleOtpChange = (e, index) => {
    const value = e.target.value;
    if (value.length > 1) return; // Allow only single characters

    let otp = formData.otp.split('');
    otp[index] = value;
    setFormData({ ...formData, otp: otp.join('') });

    // Move focus to the next input if the current one is filled
    if (value && index < 5) {
      document.getElementById(`otp-input-${index + 1}`).focus();
    }
  };

  const handleBackspace = (e, index) => {
    if (e.key === 'Backspace' && !formData.otp[index]) {
      // Move focus to the previous input when backspace is pressed
      if (index > 0) {
        document.getElementById(`otp-input-${index - 1}`).focus();
      }
    }
  };

  const handlePasteOtp = (e) => {
    const pastedValue = e.clipboardData.getData('Text').slice(0, 6); // Ensure it doesn't exceed 6 characters
    setFormData({ ...formData, otp: pastedValue });
    const otpLength = pastedValue.length;

    for (let i = 0; i < otpLength; i++) {
      document.getElementById(`otp-input-${i}`).value = pastedValue[i];
    }

    // Focus on the next input after pasting
    if (otpLength < 6) {
      document.getElementById(`otp-input-${otpLength}`).focus();
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        <div className="bg-white bg-opacity-95 p-2 rounded-2xl shadow-3xl transform transition-all duration-500 hover:scale-[1.02] hover:animate-blur-fade ease-in-out">
          <div className="px-8 pt-8">
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold text-gray-800">Create Account</h2>
              <p className="text-gray-600 mt-2">Join us for personalized shopping recommendations</p>
            </div>

            {step === 1 ? (
              <motion.form onSubmit={handleInitRegistration} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Full Name</label>
                  <motion.input type="text" required className="mt-1 block w-full px-4 py-3 rounded-lg border border-gray-300" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700">Email</label>
                  <motion.input type="email" required className="mt-1 block w-full px-4 py-3 rounded-lg border border-gray-300" value={formData.email} onChange={(e) => setFormData({ ...formData, email: e.target.value })} />
                </div>

                <motion.button type="submit" disabled={isLoading} className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium shadow-lg hover:shadow-xl">
                  {isLoading ? 'Sending OTP...' : 'Continue'}
                </motion.button>
              </motion.form>
            ) : (
              <motion.form onSubmit={handleVerifyRegistration} className="space-y-6">
                <div>
                  <label className="mb-2 block text-sm font-medium text-gray-700">Enter OTP</label>
                  <div className="flex space-x-4 justify-center">
                    {Array.from({ length: 6 }).map((_, index) => (
                      <input
                        key={index}
                        id={`otp-input-${index}`}
                        type="text"
                        maxLength={1}
                        className="w-12 h-12 text-center text-xl font-semibold border rounded-lg focus:ring-2 focus:ring-purple-500 focus:outline-none"
                        value={formData.otp[index] || ''}
                        onChange={(e) => handleOtpChange(e, index)}
                        onKeyDown={(e) => handleBackspace(e, index)} // Handle backspace
                        onPaste={handlePasteOtp}
                      />
                    ))}
                  </div>
                </div>

                <div className="relative">
                  <label className="mb-2 block text-sm font-medium text-gray-700">Password</label>
                  <motion.input type={showPassword ? 'text' : 'password'} required className="mt-1 block w-full px-4 py-3 rounded-lg border border-gray-300" value={formData.password} onChange={(e) => setFormData({ ...formData, password: e.target.value })} />
                  <button type="button" onClick={togglePasswordVisibility} className="absolute right-3 top-9 text-gray-500 hover:text-gray-700 focus:outline-none">
                    {showPassword ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
                  </button>
                </div>

                <div className="relative">
                  <label className="mb-2 block text-sm font-medium text-gray-700">Confirm Password</label>
                  <motion.input type={showConfirmPassword ? 'text' : 'password'} required className="mt-1 block w-full px-4 py-3 rounded-lg border border-gray-300" value={formData.confirmPassword} onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })} />
                  <button type="button" onClick={toggleConfirmPasswordVisibility} className="absolute right-3 top-9 text-gray-500 hover:text-gray-700 focus:outline-none">
                    {showConfirmPassword ? <Eye className="h-5 w-5" /> : <EyeOff className="h-5 w-5" />}
                  </button>
                </div>

                <motion.button type="submit" disabled={isLoading} className="w-full py-3 px-4 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium shadow-lg hover:shadow-xl">
                  {isLoading ? 'Creating account...' : 'Create Account'}
                </motion.button>
              </motion.form>
            )}

            <div className="mt-6 text-center mb-8">
              <p className="text-gray-600">
                Already have an account?{' '}
                <Link to="/login" className="text-purple-600 hover:text-purple-500 font-medium">Sign in</Link>
              </p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Register;

