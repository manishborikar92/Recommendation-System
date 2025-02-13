import React, { useEffect, useRef, useState } from 'react';
import { useWindowSize } from '@react-hook/window-size';

const OTPInput = ({ 
  value, 
  onChange, 
  error, 
  onResend,
  resendable = true,
  countdown = 60,
  autoSubmit
}) => {
  const [width] = useWindowSize();
  const inputsRef = useRef([]);
  const [timeLeft, setTimeLeft] = useState(countdown);
  const isMobile = width < 640;

  const handleChange = (e, index) => {
    const newOtp = [...value];
    newOtp[index] = e.target.value.replace(/\D/g, '');
    const otpString = newOtp.join('');
    
    onChange(otpString);
    
    if (e.target.value && index < 5) {
      inputsRef.current[index + 1].focus();
    }

    if (otpString.length === 6 && autoSubmit) {
      autoSubmit();
    }
  };

  const handleKeyDown = (e, index) => {
    if (e.key === 'Backspace') {
      if (!value[index] && index > 0) {
        inputsRef.current[index - 1].focus();
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputsRef.current[index - 1].focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputsRef.current[index + 1].focus();
    }
  };

  const handlePaste = (e) => {
    e.preventDefault();
    const pasteData = e.clipboardData.getData('text/plain').slice(0, 6).replace(/\D/g, '');
    const newOtp = [...value];
    pasteData.split('').forEach((char, i) => {
      if (i < 6) newOtp[i] = char;
    });
    onChange(newOtp.join(''));
  };

  const startCountdown = () => {
    if (onResend) {
      setTimeLeft(countdown);
      onResend();
    }
  };

  useEffect(() => {
    if (value.length === 0) {
      inputsRef.current[0].focus();
    }
  }, [value]);

  useEffect(() => {
    const timer = timeLeft > 0 && setInterval(() => {
      setTimeLeft(timeLeft - 1);
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft]);

  return (
    <div className="space-y-3">
      <div className="flex flex-col items-center gap-1.5">
        <label className="block text-sm sm:text-[0.9375rem] font-medium text-gray-700 text-center">
          Verification Code
        </label>
        
        <div className="flex justify-center gap-1 sm:gap-2">
          {Array.from({ length: 6 }).map((_, index) => (
            <input
              key={index}
              ref={(el) => (inputsRef.current[index] = el)}
              type="text"
              inputMode="numeric"
              pattern="[0-9]*"
              maxLength={1}
              value={value[index] || ''}
              onChange={(e) => handleChange(e, index)}
              onKeyDown={(e) => handleKeyDown(e, index)}
              onPaste={handlePaste}
              className={`text-center font-semibold border-2 rounded-md sm:rounded-lg transition-all 
                focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none
                flex-1 max-w-[3.5rem] min-w-[2rem] h-10 sm:h-14
                text-xl sm:text-2xl
                ${error ? 'border-red-500 shake-animation' : 'border-gray-200 hover:border-blue-300'}
                ${value[index] ? 'bg-blue-50 border-blue-400' : ''}`}
              aria-label={`Digit ${index + 1} of 6 digit verification code`}
            />
          ))}
        </div>

        {error && (
          <p className="text-sm sm:text-[0.9375rem] text-red-600 flex items-center gap-1 mt-1.5">
            <svg className="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            <span>{error}</span>
          </p>
        )}
      </div>

      {onResend && (
        <div className="text-center text-sm sm:text-[0.9375rem] text-gray-600">
          {timeLeft > 0 ? (
            <span>
              Resend in{' '}
              <span className="font-semibold text-blue-600">{timeLeft}s</span>
            </span>
          ) : (
            <button
              type="button"
              onClick={startCountdown}
              disabled={!resendable}
              className={`font-semibold ${
                resendable 
                  ? 'text-blue-600 hover:text-blue-500 cursor-pointer'
                  : 'text-gray-400 cursor-not-allowed'
              } transition-colors px-2 py-1 rounded-md`}
            >
              Resend OTP
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default OTPInput