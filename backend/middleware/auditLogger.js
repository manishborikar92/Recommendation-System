// backend/middleware/auditLogger.js
const winston = require('winston');
const { v4: uuidv4 } = require('uuid');
const fs = require('fs');

// Create logs directory if not exists
if (!fs.existsSync('logs')) fs.mkdirSync('logs');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ 
      filename: 'logs/audit.log',
      maxsize: 5 * 1024 * 1024, // 5MB
      maxFiles: 3
    })
  ]
});

const auditLog = (req, res, next) => {
  const logId = uuidv4();
  const startTime = Date.now();

  res.on('finish', () => {
    const logData = {
      logId,
      timestamp: new Date().toISOString(),
      method: req.method,
      path: req.path,
      ip: req.ip,
      userId: req.user?.id || 'anonymous',
      statusCode: res.statusCode,
      durationMs: Date.now() - startTime
    };

    logger.info('API Request', logData);
  });

  next();
};

module.exports = auditLog;