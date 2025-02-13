// routes/auth.js
const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const crypto = require('crypto');
const User = require('../models/User');
const TemporaryRegistration = require('../models/TemporaryRegistration');
const { sendOTPEmail } = require('../utils/emailService');

// Validate environment variables
['JWT_SECRET', 'OTP_SECRET', 'SALT_ROUNDS', 'OTP_EXPIRY_MINUTES'].forEach(varName => {
  if (!process.env[varName]) throw new Error(`Missing required environment variable: ${varName}`);
});

// Configuration
const CONFIG = {
  OTP_EXPIRY_MINUTES: parseInt(process.env.OTP_EXPIRY_MINUTES),
  OTP_LENGTH: 6,
  SALT_ROUNDS: parseInt(process.env.SALT_ROUNDS),
  TOKEN_EXPIRATION: '1h',
  PASSWORD_MIN_LENGTH: 8,
  MAX_OTP_ATTEMPTS: 3
};

// Validation schemas
const validations = {
  registration: [
    body('name')
      .trim()
      .notEmpty().withMessage('Name is required')
      .isLength({ min: 2 }).withMessage('Name must be at least 2 characters'),
    body('email')
      .trim()
      .isEmail().withMessage('Valid email is required')
      .normalizeEmail()
  ],

  password: [
    body('password')
      .isLength({ min: CONFIG.PASSWORD_MIN_LENGTH })
      .withMessage(`Password must be at least ${CONFIG.PASSWORD_MIN_LENGTH} characters`)
      .matches(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/)
      .withMessage('Password must contain at least one uppercase letter, one lowercase letter, and one number'),
    body('confirmPassword')
      .custom((value, { req }) => value === req.body.password)
      .withMessage('Passwords do not match')
  ],

  otp: [
    body('otp')
      .trim()
      .isLength({ min: CONFIG.OTP_LENGTH, max: CONFIG.OTP_LENGTH })
      .withMessage(`OTP must be ${CONFIG.OTP_LENGTH} characters`)
      .isAlphanumeric()
  ]
};

// Helper functions
const helpers = {
  generateOTP: () => [...crypto.randomBytes(CONFIG.OTP_LENGTH)]
    .map(byte => byte % 10)
    .join(''),

  hashData: (data) => crypto
    .createHmac('sha256', process.env.OTP_SECRET)
    .update(data)
    .digest('hex'),

  generateToken: (user) => jwt.sign(
    { userId: user._id, email: user.email, tv: user.tokenVersion },
    process.env.JWT_SECRET,
    { expiresIn: CONFIG.TOKEN_EXPIRATION }
  ),

  handleError: (res, error, message = 'An error occurred') => {
    console.error(`Error: ${message}`, error);
    const status = error.statusCode || 500;
    res.status(status).json({ 
      error: process.env.NODE_ENV === 'production' ? message : error.message 
    });
  }
};

// Registration Init
router.post('/register/init', 
  validations.registration,
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

      const { name, email } = req.body;

      // Check existing verified user
      const existingUser = await User.findOne({ email });
      if (existingUser) return res.status(409).json({ error: 'Email already registered' });

      // Generate OTP
      const otp = helpers.generateOTP();
      const otpHash = helpers.hashData(otp);
      const otpExpiry = new Date(Date.now() + CONFIG.OTP_EXPIRY_MINUTES * 60000);

      // Rate limiting
      const recentRequest = await TemporaryRegistration.findOne({ 
        email, 
        createdAt: { $gt: new Date(Date.now() - 60000) } 
      });
      if (recentRequest) return res.status(429).json({ error: 'Please wait before requesting new OTP' });

      // Upsert temporary registration
      await TemporaryRegistration.findOneAndUpdate(
        { email },
        { name, email, otp: otpHash, otpExpiry, $setOnInsert: { createdAt: new Date() } },
        { upsert: true, new: true }
      );

      await sendOTPEmail(email, otp, CONFIG.OTP_EXPIRY_MINUTES);
      res.json({ message: 'OTP sent successfully' });
    } catch (error) {
      helpers.handleError(res, error, 'Registration initiation failed');
    }
  }
);

// Registration Verify
router.post('/register/verify',
  [...validations.password, ...validations.otp],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

      const { email, otp, password } = req.body;

      // Find temporary registration
      const tempReg = await TemporaryRegistration.findOneAndUpdate(
        { email },
        { $inc: { otpAttempts: 1 } },
        { new: true }
      );

      if (!tempReg) return res.status(400).json({ error: 'Invalid verification request' });
      if (tempReg.otpAttempts > CONFIG.MAX_OTP_ATTEMPTS) {
        return res.status(429).json({ error: 'Too many attempts. Request new OTP' });
      }

      // Verify OTP
      const otpHash = helpers.hashData(otp);
      if (otpHash !== tempReg.otp || Date.now() > tempReg.otpExpiry) {
        return res.status(401).json({ error: 'Invalid or expired OTP' });
      }

      // Create user
      const user = new User({ 
        name: tempReg.name, 
        email: tempReg.email, 
        password 
      });
      
      await user.save();
      await TemporaryRegistration.deleteOne({ email });

      const token = helpers.generateToken(user);
      res.status(201).json({
        userId: user._id,
        name: user.name,
        email: user.email,
        token,
        expiresIn: CONFIG.TOKEN_EXPIRATION
      });
    } catch (error) {
      helpers.handleError(res, error, 'Registration verification failed');
    }
  }
);

// Updated Login Route
router.post('/login',
  [
    body('email').trim().isEmail().normalizeEmail(),
    body('password').notEmpty()
  ],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

      const { email, password } = req.body;
      const user = await User.findOne({ email }).select('+password');
      
      if (!user || !(await bcrypt.compare(password, user.password))) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      const token = helpers.generateToken(user);
      res.json({
        userId: user._id,
        name: user.name,
        email: user.email,
        token,
        expiresIn: CONFIG.TOKEN_EXPIRATION
      });
    } catch (error) {
      helpers.handleError(res, error, 'Authentication failed');
    }
  }
);

// Updated Password Reset Init
router.post('/password-reset/init',
  [body('email').trim().isEmail().normalizeEmail()],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

      const { email } = req.body;
      const user = await User.findOne({ email });
      
      // Generic response regardless of user existence
      const response = {
        message: 'If the email exists, an OTP will be sent',
        expiresIn: CONFIG.OTP_EXPIRY_MINUTES * 60
      };

      if (!user) return res.status(200).json(response);

      // Rate limiting check
      if (user.resetOtpExpiry && Date.now() < user.resetOtpExpiry.getTime() + 60000) {
        return res.status(429).json({ 
          error: 'Please wait before requesting another OTP',
          retryAfter: 60
        });
      }

      const otp = helpers.generateOTP();
      const resetOtpHash = helpers.hashData(otp);
      const resetOtpExpiry = new Date(Date.now() + CONFIG.OTP_EXPIRY_MINUTES * 60000);

      user.resetOtp = resetOtpHash;
      user.resetOtpExpiry = resetOtpExpiry;
      user.resetOtpAttempts = 0;
      await user.save();

      await sendOTPEmail(email, otp, CONFIG.OTP_EXPIRY_MINUTES);
      res.status(200).json(response);
    } catch (error) {
      helpers.handleError(res, error, 'Failed to process password reset');
    }
  }
);

// Updated Password Reset Verify
router.post('/password-reset/verify',
  [...validations.password, ...validations.otp],
  async (req, res) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

      const { email, otp, password } = req.body;
      const user = await User.findOne({ email });

      if (!user) return res.status(400).json({ error: 'Invalid reset request' });

      // Check attempts
      if (user.resetOtpAttempts >= CONFIG.MAX_OTP_ATTEMPTS) {
        return res.status(429).json({ 
          error: 'Too many failed attempts. Please request a new OTP'
        });
      }

      // Verify OTP
      const resetOtpHash = helpers.hashData(otp);
      if (resetOtpHash !== user.resetOtp || Date.now() > user.resetOtpExpiry) {
        user.resetOtpAttempts += 1;
        await user.save();
        return res.status(401).json({ error: 'Invalid or expired OTP' });
      }

      // Update password and clear reset fields
      user.password = password; // Will be hashed by pre-save hook
      user.resetOtp = undefined;
      user.resetOtpExpiry = undefined;
      user.resetOtpAttempts = undefined;
      user.tokenVersion += 1;
      await user.save();

      res.status(200).json({ message: 'Password reset successfully' });
    } catch (error) {
      helpers.handleError(res, error, 'Failed to reset password');
    }
  }
);

module.exports = router;