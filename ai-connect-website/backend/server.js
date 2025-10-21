const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path');
const rateLimit = require('express-rate-limit');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// ===================================
//   Middleware Setup
// ===================================

// Security middleware
app.use(helmet({
    contentSecurityPolicy: {
        directives: {
            defaultSrc: ["'self'"],
            styleSrc: ["'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com"],
            fontSrc: ["'self'", "https://fonts.gstatic.com", "https://cdnjs.cloudflare.com"],
            scriptSrc: ["'self'", "'unsafe-inline'"],
            imgSrc: ["'self'", "data:", "https:"],
            connectSrc: ["'self'", "https://api.openai.com"]
        }
    }
}));

// CORS configuration
const corsOptions = {
    origin: process.env.CORS_ORIGIN || ['http://localhost:3000', 'http://127.0.0.1:3000'],
    credentials: true,
    optionsSuccessStatus: 200
};
app.use(cors(corsOptions));

// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: {
        error: 'Too many requests from this IP, please try again later.',
        retryAfter: '15 minutes'
    }
});
app.use('/api/', limiter);

// Chatbot specific rate limiting
const chatbotLimiter = rateLimit({
    windowMs: 1 * 60 * 1000, // 1 minute
    max: 10, // limit each IP to 10 chatbot requests per minute
    message: {
        error: 'Too many chatbot requests, please slow down.',
        retryAfter: '1 minute'
    }
});

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Static file serving
app.use(express.static(path.join(__dirname, '../frontend')));

// Request logging
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path} - ${req.ip}`);
    next();
});

// ===================================
//   API Routes
// ===================================

// Health check endpoint
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0',
        environment: process.env.NODE_ENV || 'development'
    });
});

// Import route modules
const chatbotRoutes = require('./routes/chatbot');
const contactRoutes = require('./routes/contact');

app.use('/api/chatbot', chatbotLimiter, chatbotRoutes);
app.use('/api/contact', contactRoutes);

// ===================================
//   Frontend Routes
// ===================================

// Serve HTML pages
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

app.get('/about', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/about.html'));
});

app.get('/contact', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/contact.html'));
});

app.get('/blog', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/blog.html'));
});

app.get('/chatbot', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/chatbot.html'));
});

// Catch-all handler for SPA-style routing
app.get('*', (req, res) => {
    // Check if it's an API request that wasn't found
    if (req.path.startsWith('/api/')) {
        return res.status(404).json({
            error: 'API endpoint not found',
            path: req.path,
            method: req.method
        });
    }
    
    // For all other routes, serve the homepage
    res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

// ===================================
//   Error Handling
// ===================================

// 404 Error Handler
app.use((req, res) => {
    if (req.path.startsWith('/api/')) {
        res.status(404).json({
            error: 'API endpoint not found',
            path: req.path,
            method: req.method,
            timestamp: new Date().toISOString()
        });
    } else {
        res.status(404).sendFile(path.join(__dirname, '../frontend/index.html'));
    }
});

// Global Error Handler
app.use((error, req, res, next) => {
    console.error('Server Error:', error);
    
    // Don't leak error details in production
    const isDevelopment = process.env.NODE_ENV === 'development';
    
    const errorResponse = {
        error: 'Internal server error',
        timestamp: new Date().toISOString(),
        path: req.path,
        method: req.method
    };
    
    if (isDevelopment) {
        errorResponse.details = error.message;
        errorResponse.stack = error.stack;
    }
    
    res.status(error.status || 500).json(errorResponse);
});

// ===================================
//   Server Startup
// ===================================

// Graceful shutdown handling
const server = app.listen(PORT, () => {
    console.log(`🚀 AI Connect server running on port ${PORT}`);
    console.log(`📱 Frontend: http://localhost:${PORT}`);
    console.log(`🔧 API: http://localhost:${PORT}/api`);
    console.log(`🌍 Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`⏰ Started at: ${new Date().toISOString()}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('🛑 SIGTERM received, shutting down gracefully...');
    server.close(() => {
        console.log('✅ Server closed successfully');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('🛑 SIGINT received, shutting down gracefully...');
    server.close(() => {
        console.log('✅ Server closed successfully');
        process.exit(0);
    });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('💥 Uncaught Exception:', error);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('💥 Unhandled Rejection at:', promise, 'reason:', reason);
    process.exit(1);
});

module.exports = app;