// backend/middleware/security.js
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

// Security headers
const securityHeaders = helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https://*.amazonaws.com"]
    }
  },
  crossOriginEmbedderPolicy: false
});

// Auth endpoint rate limiting
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 20, // 20 requests per window
  message: 'Too many attempts from this IP, please try again later',
  standardHeaders: true,
  legacyHeaders: false
});

module.exports = { securityHeaders, authLimiter };