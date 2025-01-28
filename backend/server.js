// backend/server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const connectDB = require('./config/db');
const compression = require('compression'); // Missing dependency
const { securityHeaders, authLimiter } = require('./middleware/security');
const auditLog = require('./middleware/auditLogger');

// Initialize Express
const app = express();

// 1. Database Connection
connectDB();

// 2. Middleware (CRITICAL ORDER!)
app.use(securityHeaders); // Security headers first
app.use(auditLog); // Logging before other middleware
app.use(compression()); // Add compression for performance
app.use(cors({
  origin: process.env.CLIENT_URL || 'http://localhost:5173',
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  credentials: true
}));

// 3. Body Parsers
app.use(express.json({ limit: '10kb' })); // Add payload limit
app.use(express.urlencoded({ extended: true, limit: '10kb' }));

// 4. Rate Limiting
app.use('/api/auth', authLimiter);

// 5. Routes
const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);
// const recommendRoutes = require("./routes/recommend");
// app.use("/api/recommend", recommendRoutes); // Add secured recommendation routes

// 6. Health Check
app.get('/api/health', (req, res) => {
  res.json({ 
    status: 'active', 
    services: {
      database: 'connected',
      ml_service: 'inactive'
    },
    uptime: process.uptime()
  });
});

// 7. Handle 404s (Missing in original)
app.use('*', (req, res) => {
  res.status(404).json({
    status: 'fail',
    message: `Can't find ${req.originalUrl} on this server`
  });
});

// 8. Error Handling (Improved)
app.use((err, req, res, next) => {
  err.statusCode = err.statusCode || 500;
  err.status = err.status || 'error';

  res.status(err.statusCode).json({
    status: err.status,
    message: err.message,
    ...(process.env.NODE_ENV === 'development' && { stack: err.stack })
  });
});

// 9. Server Configuration
const PORT = process.env.PORT || 5000;
const env = process.env.NODE_ENV || 'development';

app.listen(PORT, () => {
  console.log(`Server running in ${env} mode on port ${PORT}`);
});

