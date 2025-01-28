const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { body, validationResult } = require('express-validator');
const User = require('../models/User');
const crypto = require('crypto');
const { sendPasswordResetEmail } = require('../utils/emailService');

// Registration Endpoint
router.post('/register', 
  [
    body('email').isEmail().normalizeEmail(),
    body('password').isLength({ min: 6 }),
    body('username').trim().notEmpty()
  ],
  async (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

    try {
      const { email, password, username } = req.body;
      
      // Check existing user
      const existingUser = await User.findOne({ email });
      if (existingUser) {
        return res.status(409).json({ error: 'User already exists' });
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, 12);
      
      const user = await User.create({
        email,
        username,
        password: hashedPassword
      });
      
      // Generate JWT
      const token = jwt.sign(
        { userId: user._id, email: user.email },
        process.env.JWT_SECRET || 'development_secret',
        { expiresIn: '1h' }
      );

      res.status(201).json({ userId: user._id, token });

    } catch (error) {
      console.error('Registration error:', error);
      res.status(500).json({ error: 'Server error during registration' });
    }
  }
);

// Login Endpoint
router.post('/login', async (req, res) => {
  const { email, password } = req.body;
  
  try {
    const user = await User.findOne({ email }).select('+password');
    if (!user) return res.status(401).json({ error: 'Invalid credentials' });

    const isValid = await bcrypt.compare(password, user.password);
    if (!isValid) return res.status(401).json({ error: 'Invalid credentials' });

    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET || 'development_secret',
      { expiresIn: '1h' }
    );

    res.json({ userId: user._id, token });
    
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ error: 'Server error during login' });
  }
});

// Forgot Password Endpoint
router.post('/forgot-password', 
  body('email').isEmail().normalizeEmail(),
  async (req, res) => {
    try {
      const user = await User.findOne({ email: req.body.email });
      if (!user) return res.status(404).json({ error: 'User not found' });

      // Generate reset token (32 bytes = 64 hex chars)
      const resetToken = crypto.randomBytes(32).toString('hex');
      
      // Set expiration (1 hour)
      user.resetPasswordToken = crypto
        .createHash('sha256')
        .update(resetToken)
        .digest('hex');
      user.resetPasswordExpire = Date.now() + 3600000; // 1 hour
      
      await user.save({ validateBeforeSave: false });
      
      // Send email with original token (not hashed)
      await sendPasswordResetEmail(user.email, resetToken);
      
      res.status(200).json({ message: 'Reset email sent' });

    } catch (error) {
      user.resetPasswordToken = undefined;
      user.resetPasswordExpire = undefined;
      await user.save({ validateBeforeSave: false });
      res.status(500).json({ error: 'Password reset failed' });
    }
  }
);

// Reset Password Endpoint
router.post('/reset-password',
  [
    body('token').notEmpty(),
    body('password').isLength({ min: 6 })
  ],
  async (req, res) => {
    try {
      // Hash token for DB comparison
      const hashedToken = crypto
        .createHash('sha256')
        .update(req.body.token)
        .digest('hex');

      const user = await User.findOne({
        resetPasswordToken: hashedToken,
        resetPasswordExpire: { $gt: Date.now() }
      });

      if (!user) return res.status(400).json({ error: 'Invalid or expired token' });

      user.password = await bcrypt.hash(req.body.password, 12);
      user.resetPasswordToken = undefined;
      user.resetPasswordExpire = undefined;
      
      await user.save();
      res.status(200).json({ message: 'Password updated successfully' });

    } catch (error) {
      res.status(500).json({ error: 'Password reset failed' });
    }
  }
);

module.exports = router;