// utils/emailService.js
const nodemailer = require('nodemailer');
const path = require('path');
const fs = require('fs').promises;
const handlebars = require('handlebars');

const transport = nodemailer.createTransport({
  service: 'gmail',
  auth: {
    user: process.env.GMAIL_USER,
    pass: process.env.GMAIL_APP_PASSWORD
  },
  pool: true,
  rateLimit: true,
  maxConnections: 5,
  maxMessages: 100
});

const templateCache = new Map();

async function loadTemplate(name) {
  if (templateCache.has(name)) return templateCache.get(name);
  
  const filePath = path.join(__dirname, `../templates/email/${name}.hbs`);
  const source = await fs.readFile(filePath, 'utf-8');
  const template = handlebars.compile(source);
  templateCache.set(name, template);
  return template;
}

async function sendOTPEmail(email, otp, expiryMinutes) {
  try {
    const template = await loadTemplate('otp');
    const html = template({ otp, expiryMinutes });
    
    await transport.sendMail({
      from: `"Virtual Vangaurds" <${process.env.EMAIL_FROM}>`,
      to: email,
      subject: 'Your Verification Code',
      html,
      headers: { 'X-OTP-Context': 'registration' }
    });
  } catch (error) {
    console.error('OTP Email Failed:', { email, error });
    throw new Error('Failed to send OTP email');
  }
}

module.exports = { sendOTPEmail };