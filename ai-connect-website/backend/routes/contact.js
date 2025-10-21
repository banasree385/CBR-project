const express = require('express');
const router = express.Router();
const nodemailer = require('nodemailer');

// ===================================
//   Email Configuration
// ===================================

let transporter = null;

// Initialize email transporter
function initializeEmailTransporter() {
    if (process.env.EMAIL_USER && process.env.EMAIL_PASS) {
        transporter = nodemailer.createTransport({
            service: process.env.EMAIL_SERVICE || 'gmail',
            auth: {
                user: process.env.EMAIL_USER,
                pass: process.env.EMAIL_PASS
            },
            tls: {
                rejectUnauthorized: false
            }
        });
        
        // Verify connection
        transporter.verify((error, success) => {
            if (error) {
                console.error('❌ Email configuration error:', error);
                transporter = null;
            } else {
                console.log('✅ Email service ready');
            }
        });
    } else {
        console.warn('⚠️  Email credentials not configured. Contact form will use mock responses.');
    }
}

// Initialize on module load
initializeEmailTransporter();

// ===================================
//   Contact Form Handler
// ===================================

router.post('/', async (req, res) => {
    try {
        const { name, email, phone, company, subject, message, newsletter } = req.body;
        
        // Validation
        const validation = validateContactForm(req.body);
        if (!validation.isValid) {
            return res.status(400).json({
                error: 'Validation failed',
                details: validation.errors
            });
        }
        
        // Log the contact form submission
        console.log(`📧 Contact form submission from: ${name} (${email})`);
        
        if (transporter) {
            // Send actual emails
            await sendContactEmails(req.body);
        } else {
            // Mock email sending
            console.log('📧 Mock: Contact email would be sent');
        }
        
        // If newsletter subscription is requested
        if (newsletter) {
            await handleNewsletterSubscription(email, name);
        }
        
        res.json({
            success: true,
            message: 'Thank you for your message! We will get back to you within 24 hours.',
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Contact form error:', error);
        res.status(500).json({
            error: 'Failed to send message. Please try again or contact us directly.',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
});

// ===================================
//   Newsletter Subscription
// ===================================

router.post('/newsletter', async (req, res) => {
    try {
        const { email } = req.body;
        
        if (!email || !isValidEmail(email)) {
            return res.status(400).json({
                error: 'Valid email address is required'
            });
        }
        
        await handleNewsletterSubscription(email);
        
        res.json({
            success: true,
            message: 'Successfully subscribed to our newsletter!',
            timestamp: new Date().toISOString()
        });
        
    } catch (error) {
        console.error('Newsletter subscription error:', error);
        res.status(500).json({
            error: 'Failed to subscribe to newsletter. Please try again.'
        });
    }
});

// ===================================
//   Validation Functions
// ===================================

function validateContactForm(data) {
    const errors = [];
    
    // Required fields
    if (!data.name || data.name.trim().length < 2) {
        errors.push('Name must be at least 2 characters long');
    }
    
    if (!data.email || !isValidEmail(data.email)) {
        errors.push('Valid email address is required');
    }
    
    if (!data.subject || data.subject.trim().length === 0) {
        errors.push('Subject is required');
    }
    
    if (!data.message || data.message.trim().length < 10) {
        errors.push('Message must be at least 10 characters long');
    }
    
    // Optional field validation
    if (data.phone && !isValidPhone(data.phone)) {
        errors.push('Invalid phone number format');
    }
    
    // Length limits
    if (data.name && data.name.length > 100) {
        errors.push('Name is too long (maximum 100 characters)');
    }
    
    if (data.company && data.company.length > 100) {
        errors.push('Company name is too long (maximum 100 characters)');
    }
    
    if (data.message && data.message.length > 1000) {
        errors.push('Message is too long (maximum 1000 characters)');
    }
    
    return {
        isValid: errors.length === 0,
        errors: errors
    };
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function isValidPhone(phone) {
    // Remove common phone number formatting
    const cleanPhone = phone.replace(/[\s\-\(\)\+]/g, '');
    // Check if it's a valid phone number (10-15 digits)
    return /^\d{10,15}$/.test(cleanPhone);
}

// ===================================
//   Email Sending Functions
// ===================================

async function sendContactEmails(formData) {
    const { name, email, phone, company, subject, message } = formData;
    
    // Email to admin
    const adminEmail = {
        from: process.env.EMAIL_USER,
        to: process.env.EMAIL_USER,
        subject: `Contact Form: ${subject}`,
        html: generateAdminEmailHTML(formData),
        text: generateAdminEmailText(formData)
    };
    
    // Confirmation email to user
    const userEmail = {
        from: process.env.EMAIL_USER,
        to: email,
        subject: 'Thank you for contacting AI Connect',
        html: generateUserConfirmationHTML(name),
        text: generateUserConfirmationText(name)
    };
    
    // Send both emails
    await Promise.all([
        transporter.sendMail(adminEmail),
        transporter.sendMail(userEmail)
    ]);
    
    console.log(`✅ Contact emails sent successfully to ${email}`);
}

async function handleNewsletterSubscription(email, name = '') {
    if (transporter) {
        const welcomeEmail = {
            from: process.env.EMAIL_USER,
            to: email,
            subject: 'Welcome to AI Connect Newsletter',
            html: generateNewsletterWelcomeHTML(name),
            text: generateNewsletterWelcomeText(name)
        };
        
        await transporter.sendMail(welcomeEmail);
        console.log(`✅ Newsletter welcome email sent to ${email}`);
    } else {
        console.log(`📧 Mock: Newsletter subscription for ${email}`);
    }
}

// ===================================
//   Email Template Functions
// ===================================

function generateAdminEmailHTML(formData) {
    const { name, email, phone, company, subject, message } = formData;
    
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .header { background: #2563eb; color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; background: #f9f9f9; }
                .field { margin-bottom: 15px; }
                .label { font-weight: bold; color: #2563eb; }
                .value { margin-left: 10px; }
                .message-box { background: white; padding: 15px; border-left: 4px solid #2563eb; margin-top: 15px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🤖 New Contact Form Submission - AI Connect</h2>
            </div>
            <div class="content">
                <div class="field">
                    <span class="label">From:</span>
                    <span class="value">${escapeHtml(name)} &lt;${escapeHtml(email)}&gt;</span>
                </div>
                <div class="field">
                    <span class="label">Subject:</span>
                    <span class="value">${escapeHtml(subject)}</span>
                </div>
                ${phone ? `<div class="field"><span class="label">Phone:</span><span class="value">${escapeHtml(phone)}</span></div>` : ''}
                ${company ? `<div class="field"><span class="label">Company:</span><span class="value">${escapeHtml(company)}</span></div>` : ''}
                <div class="field">
                    <span class="label">Submitted:</span>
                    <span class="value">${new Date().toLocaleString()}</span>
                </div>
                <div class="message-box">
                    <div class="label">Message:</div>
                    <div style="margin-top: 10px;">${escapeHtml(message).replace(/\\n/g, '<br>')}</div>
                </div>
            </div>
        </body>
        </html>
    `;
}

function generateAdminEmailText(formData) {
    const { name, email, phone, company, subject, message } = formData;
    
    return `
New Contact Form Submission - AI Connect

From: ${name} <${email}>
Subject: ${subject}
${phone ? `Phone: ${phone}` : ''}
${company ? `Company: ${company}` : ''}
Submitted: ${new Date().toLocaleString()}

Message:
${message}
    `.trim();
}

function generateUserConfirmationHTML(name) {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
                .container { max-width: 600px; margin: 0 auto; background: white; }
                .header { background: linear-gradient(135deg, #2563eb, #06b6d4); color: white; padding: 30px; text-align: center; }
                .content { padding: 30px; }
                .footer { background: #f8fafc; padding: 20px; text-align: center; font-size: 14px; color: #666; }
                .logo { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
                .btn { display: inline-block; background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🤖 AI Connect</div>
                    <h2>Thank you for contacting us!</h2>
                </div>
                <div class="content">
                    <p>Hi ${escapeHtml(name)},</p>
                    <p>Thank you for reaching out to AI Connect! We've received your message and appreciate your interest in our AI solutions.</p>
                    <p><strong>What happens next?</strong></p>
                    <ul>
                        <li>Our team will review your message within 24 hours</li>
                        <li>We'll respond to your inquiry with relevant information</li>
                        <li>If needed, we'll schedule a consultation to discuss your needs</li>
                    </ul>
                    <p>In the meantime, feel free to explore our website to learn more about our AI chatbot solutions and how they can benefit your business.</p>
                    <a href="${process.env.CORS_ORIGIN || 'http://localhost:3000'}" class="btn">Visit AI Connect</a>
                    <p>Best regards,<br>The AI Connect Team</p>
                </div>
                <div class="footer">
                    <p>AI Connect - Empowering the future with intelligent AI solutions</p>
                    <p>This is an automated confirmation email. Please do not reply to this message.</p>
                </div>
            </div>
        </body>
        </html>
    `;
}

function generateUserConfirmationText(name) {
    return `
Hi ${name},

Thank you for reaching out to AI Connect! We've received your message and appreciate your interest in our AI solutions.

What happens next?
- Our team will review your message within 24 hours
- We'll respond to your inquiry with relevant information  
- If needed, we'll schedule a consultation to discuss your needs

In the meantime, feel free to explore our website to learn more about our AI chatbot solutions.

Best regards,
The AI Connect Team

---
AI Connect - Empowering the future with intelligent AI solutions
This is an automated confirmation email. Please do not reply to this message.
    `.trim();
}

function generateNewsletterWelcomeHTML(name) {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
                .container { max-width: 600px; margin: 0 auto; background: white; }
                .header { background: linear-gradient(135deg, #2563eb, #06b6d4); color: white; padding: 30px; text-align: center; }
                .content { padding: 30px; }
                .footer { background: #f8fafc; padding: 20px; text-align: center; font-size: 14px; color: #666; }
                .logo { font-size: 24px; font-weight: bold; margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🤖 AI Connect</div>
                    <h2>Welcome to our Newsletter!</h2>
                </div>
                <div class="content">
                    <p>${name ? `Hi ${escapeHtml(name)},` : 'Hello!'}</p>
                    <p>Welcome to the AI Connect newsletter! 🎉</p>
                    <p>You'll now receive:</p>
                    <ul>
                        <li>Latest AI technology insights and trends</li>
                        <li>Product updates and new features</li>
                        <li>Tips for maximizing your AI implementation</li>
                        <li>Industry case studies and success stories</li>
                        <li>Exclusive content and early access to new releases</li>
                    </ul>
                    <p>We're excited to keep you informed about the latest in AI innovation!</p>
                    <p>Best regards,<br>The AI Connect Team</p>
                </div>
                <div class="footer">
                    <p>You can unsubscribe at any time by clicking the unsubscribe link in our emails.</p>
                    <p>AI Connect - Empowering the future with intelligent AI solutions</p>
                </div>
            </div>
        </body>
        </html>
    `;
}

function generateNewsletterWelcomeText(name) {
    return `
${name ? `Hi ${name},` : 'Hello!'}

Welcome to the AI Connect newsletter! 🎉

You'll now receive:
- Latest AI technology insights and trends
- Product updates and new features  
- Tips for maximizing your AI implementation
- Industry case studies and success stories
- Exclusive content and early access to new releases

We're excited to keep you informed about the latest in AI innovation!

Best regards,
The AI Connect Team

---
You can unsubscribe at any time.
AI Connect - Empowering the future with intelligent AI solutions
    `.trim();
}

// ===================================
//   Utility Functions
// ===================================

function escapeHtml(text) {
    if (!text) return '';
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

module.exports = router;