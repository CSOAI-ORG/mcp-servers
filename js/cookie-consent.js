/**
 * MEOK AI Labs — GDPR Cookie Consent Banner
 * GDPR, CCPA, UK Cookie Law compliant
 */

class CookieConsent {
  constructor(options = {}) {
    this.config = {
      cookieName: 'meok_cookie_consent',
      cookieExpiry: 365,
      bannerPosition: 'bottom',
      overlay: false,
      ...options
    };
    
    this.preferences = this.getStoredPreferences();
    this.init();
  }

  getStoredPreferences() {
    const stored = document.cookie
      .split('; ')
      .find(row => row.startsWith(`${this.config.cookieName}=`));
    
    if (stored) {
      try {
        return JSON.parse(decodeURIComponent(stored.split('=')[1]));
      } catch {
        return null;
      }
    }
    return null;
  }

  savePreferences(preferences) {
    const value = encodeURIComponent(JSON.stringify(preferences));
    const expires = new Date();
    expires.setDate(expires.getDate() + this.config.cookieExpiry);
    document.cookie = `${this.config.cookieName}=${value};expires=${expires.toUTCString()};path=/;SameSite=Lax`;
    this.preferences = preferences;
  }

  init() {
    if (this.preferences) {
      this.applyPreferences();
      return;
    }
    this.showBanner();
  }

  showBanner() {
    const existing = document.getElementById('cookie-consent-banner');
    if (existing) return;

    const banner = document.createElement('div');
    banner.id = 'cookie-consent-banner';
    banner.className = `cookie-consent-banner ${this.config.bannerPosition}`;
    banner.innerHTML = `
      <div class="cookie-consent-content">
        <div class="cookie-consent-text">
          <h3>We value your privacy</h3>
          <p>
            MEOK AI Labs uses cookies to enhance your experience, analyze site traffic, 
            and personalize content. You can accept all cookies or customize your preferences.
            <a href="/cookies.html" class="cookie-link">Learn more</a>
          </p>
        </div>
        <div class="cookie-consent-actions">
          <button class="cookie-btn cookie-btn-secondary" data-action="essential">
            Essential Only
          </button>
          <button class="cookie-btn cookie-btn-secondary" data-action="preferences">
            Customize
          </button>
          <button class="cookie-btn cookie-btn-primary" data-action="accept-all">
            Accept All
          </button>
        </div>
      </div>
      <div class="cookie-preferences-panel" style="display: none;">
        <div class="cookie-category">
          <label>
            <input type="checkbox" checked disabled>
            <span><strong>Essential</strong> — Required for site operation</span>
          </label>
        </div>
        <div class="cookie-category">
          <label>
            <input type="checkbox" name="analytics">
            <span><strong>Analytics</strong> — Help us understand usage</span>
          </label>
        </div>
        <div class="cookie-category">
          <label>
            <input type="checkbox" name="marketing">
            <span><strong>Marketing</strong> — Personalized recommendations</span>
          </label>
        </div>
        <div class="cookie-actions">
          <button class="cookie-btn cookie-btn-secondary" data-action="save-preferences">
            Save Preferences
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(banner);
    this.bindEvents(banner);
    
    if (this.config.overlay) {
      this.showOverlay();
    }
  }

  bindEvents(banner) {
    banner.querySelectorAll('[data-action]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = e.target.dataset.action;
        this.handleAction(action, banner);
      });
    });
  }

  handleAction(action, banner) {
    switch (action) {
      case 'accept-all':
        this.savePreferences({
          essential: true,
          analytics: true,
          marketing: true,
          timestamp: Date.now()
        });
        this.applyPreferences();
        this.hideBanner(banner);
        break;

      case 'essential':
        this.savePreferences({
          essential: true,
          analytics: false,
          marketing: false,
          timestamp: Date.now()
        });
        this.applyPreferences();
        this.hideBanner(banner);
        break;

      case 'preferences':
        banner.querySelector('.cookie-consent-content').style.display = 'none';
        banner.querySelector('.cookie-preferences-panel').style.display = 'block';
        break;

      case 'save-preferences':
        const analytics = banner.querySelector('[name="analytics"]').checked;
        const marketing = banner.querySelector('[name="marketing"]').checked;
        this.savePreferences({
          essential: true,
          analytics,
          marketing,
          timestamp: Date.now()
        });
        this.applyPreferences();
        this.hideBanner(banner);
        break;
    }
  }

  hideBanner(banner) {
    banner.classList.add('cookie-consent-hidden');
    setTimeout(() => banner.remove(), 300);
    this.hideOverlay();
  }

  showOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'cookie-consent-overlay';
    overlay.className = 'cookie-consent-overlay';
    document.body.appendChild(overlay);
  }

  hideOverlay() {
    const overlay = document.getElementById('cookie-consent-overlay');
    if (overlay) overlay.remove();
  }

  applyPreferences() {
    const prefs = this.preferences || { essential: true, analytics: false, marketing: false };

    // Analytics scripts
    document.querySelectorAll('[data-cookie-category="analytics"]').forEach(script => {
      if (prefs.analytics) {
        const clone = script.cloneNode(true);
        clone.removeAttribute('data-cookie-category');
        document.head.appendChild(clone);
      }
    });

    // Marketing scripts
    document.querySelectorAll('[data-cookie-category="marketing"]').forEach(script => {
      if (prefs.marketing) {
        const clone = script.cloneNode(true);
        clone.removeAttribute('data-cookie-category');
        document.head.appendChild(clone);
      }
    });

    // Dispatch event for other components
    window.dispatchEvent(new CustomEvent('cookieConsentUpdated', { detail: prefs }));
  }

  hasConsent(category) {
    return this.preferences?.[category] ?? false;
  }
}

// Auto-init
document.addEventListener('DOMContentLoaded', () => {
  window.cookieConsent = new CookieConsent();
});
