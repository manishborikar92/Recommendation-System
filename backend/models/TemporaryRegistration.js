// models/TemporaryRegistration.js
const mongoose = require('mongoose');

const tempRegSchema = new mongoose.Schema({
  email: { 
    type: String, 
    required: true, 
    unique: true,
    lowercase: true,
    trim: true,
    match: [/^\w+([.-]?\w+)*@\w+([.-]?\w+)*(\.\w{2,3})+$/, 'Invalid email']
  },
  name: { type: String, required: true },
  otp: { type: String, required: true },
  otpExpiry: { type: Date, required: true },
  otpAttempts: { type: Number, default: 0 },
  createdAt: { type: Date, default: Date.now }
});

// Auto-expire after 1 hour
tempRegSchema.index({ createdAt: 1 }, { expireAfterSeconds: 3600 });

module.exports = mongoose.model('TemporaryRegistration', tempRegSchema);