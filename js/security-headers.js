/**
 * MEOK AI Labs - Security Headers Middleware
 * Implements OWASP security best practices
 */

export const securityHeaders = {
  // Prevent MIME type sniffing
  'X-Content-Type-Options': 'nosniff',
  
  // Prevent clickjacking
  'X-Frame-Options': 'SAMEORIGIN',
  
  // XSS Protection (legacy browsers)
  'X-XSS-Protection': '1; mode=block',
  
  // Referrer Policy
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  
  // Permissions Policy (restrict features)
  'Permissions-Policy': 'camera=(), microphone=(self), geolocation=(), payment=()',
  
  // Content Security Policy
  'Content-Security-Policy': [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net",
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net",
    "img-src 'self' data: https: blob:",
    "font-src 'self' https://fonts.gstatic.com",
    "connect-src 'self' https://api.meok.ai https://localhost:*",
    "frame-ancestors 'self'",
    "form-action 'self'",
    "base-uri 'self'",
    "object-src 'none'",
  ].join('; '),
  
  // Strict Transport Security (HTTPS only)
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains; preload',
  
  // Cache Control for sensitive pages
  'Cache-Control': 'no-store, no-cache, must-revalidate, proxy-revalidate',
  'Pragma': 'no-cache',
};

export function applySecurityHeaders(response) {
  const headers = new Headers(response.headers);
  
  Object.entries(securityHeaders).forEach(([key, value]) => {
    headers.set(key, value);
  });
  
  return new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers,
  });
}

// Input sanitization
export function sanitizeInput(input) {
  if (typeof input !== 'string') return input;
  
  return input
    .replace(/[<>]/g, '') // Remove < and >
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim();
}

// SQL injection prevention
export function sanitizeSQL(input) {
  if (typeof input !== 'string') return input;
  
  const dangerous = /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|ALTER|CREATE|TRUNCATE)\b)/gi;
  return input.replace(dangerous, '');
}

// XSS prevention - HTML encoding
export function escapeHTML(str) {
  const escapeMap = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  };
  
  return str.replace(/[&<>"'/]/g, char => escapeMap[char]);
}

// Validate email format
export function isValidEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}

// Validate URL
export function isValidURL(url) {
  try {
    const parsed = new URL(url);
    return ['http:', 'https:'].includes(parsed.protocol);
  } catch {
    return false;
  }
}

// Rate limiting (in-memory, use Redis in production)
const rateLimits = new Map();

export function checkRateLimit(identifier, limit = 100, windowMs = 60000) {
  const now = Date.now();
  const key = `ratelimit:${identifier}`;
  
  if (!rateLimits.has(key)) {
    rateLimits.set(key, { count: 1, resetAt: now + windowMs });
    return { allowed: true, remaining: limit - 1 };
  }
  
  const record = rateLimits.get(key);
  
  // Reset if window expired
  if (now > record.resetAt) {
    rateLimits.set(key, { count: 1, resetAt: now + windowMs });
    return { allowed: true, remaining: limit - 1 };
  }
  
  // Check limit
  if (record.count >= limit) {
    return { 
      allowed: false, 
      remaining: 0, 
      retryAfter: Math.ceil((record.resetAt - now) / 1000) 
    };
  }
  
  record.count++;
  return { allowed: true, remaining: limit - record.count };
}

// CORS configuration
export const corsConfig = {
  origin: process.env.ALLOWED_ORIGINS?.split(',') || ['https://meok.ai'],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-API-Key'],
  exposedHeaders: ['X-RateLimit-Remaining', 'X-RateLimit-Reset'],
  credentials: true,
  maxAge: 86400,
};

// Clean up rate limits periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, value] of rateLimits) {
    if (now > value.resetAt + 60000) {
      rateLimits.delete(key);
    }
  }
}, 300000); // Every 5 minutes
