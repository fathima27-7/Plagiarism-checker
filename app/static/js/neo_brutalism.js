/**
 * PlagiScan AI – Neo-Brutalism UI Interaction Engine
 * Handles responsive sidebar toggling, toast notification dispatcher,
 * keyboard search triggers, and component interactions.
 */

class NeoBrutalism {
  static init() {
    this.initSidebar();
    this.initKeyboardShortcuts();
    this.initDismissibleAlerts();
    this.initDropzones();
  }

  /* -------------------------------------------------------------------------
   * 1 & 2. Navbar & Sidebar Drawer Toggle
   * ------------------------------------------------------------------------- */
  static initSidebar() {
    const hamburgerBtn = document.querySelector('[data-nb-toggle="sidebar"]');
    const sidebar = document.querySelector('.nb-sidebar');

    if (hamburgerBtn && sidebar) {
      hamburgerBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        sidebar.classList.toggle('open');
        const isOpen = sidebar.classList.contains('open');
        hamburgerBtn.setAttribute('aria-expanded', isOpen);
      });

      // Close sidebar when clicking outside on mobile
      document.addEventListener('click', (e) => {
        if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && !hamburgerBtn.contains(e.target)) {
          sidebar.classList.remove('open');
          hamburgerBtn.setAttribute('aria-expanded', 'false');
        }
      });
    }
  }

  /* -------------------------------------------------------------------------
   * 8. Global Keyboard Shortcuts (Ctrl/Cmd + K for Search Bar)
   * ------------------------------------------------------------------------- */
  static initKeyboardShortcuts() {
    const searchInput = document.querySelector('.nb-search-input');
    if (!searchInput) return;

    window.addEventListener('keydown', (e) => {
      // Check for Ctrl+K or Cmd+K
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        searchInput.focus();
        searchInput.select();
      }
    });
  }

  /* -------------------------------------------------------------------------
   * 9. Dismissible Banner Alerts
   * ------------------------------------------------------------------------- */
  static initDismissibleAlerts() {
    document.querySelectorAll('[data-nb-dismiss="alert"]').forEach(btn => {
      btn.addEventListener('click', () => {
        const alertBox = btn.closest('.nb-alert');
        if (alertBox) {
          alertBox.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
          alertBox.style.opacity = '0';
          alertBox.style.transform = 'translateY(-8px)';
          setTimeout(() => alertBox.remove(), 200);
        }
      });
    });
  }

  /* -------------------------------------------------------------------------
   * 7. Drag and Drop File Input Highlighting
   * ------------------------------------------------------------------------- */
  static initDropzones() {
    document.querySelectorAll('.nb-file-dropzone').forEach(dropzone => {
      const fileInput = dropzone.querySelector('input[type="file"]');

      ['dragenter', 'dragover'].forEach(name => {
        dropzone.addEventListener(name, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.add('dragover');
        });
      });

      ['dragleave', 'drop'].forEach(name => {
        dropzone.addEventListener(name, (e) => {
          e.preventDefault();
          e.stopPropagation();
          dropzone.classList.remove('dragover');
        });
      });

      dropzone.addEventListener('click', () => {
        if (fileInput) fileInput.click();
      });
    });
  }
}

/* -------------------------------------------------------------------------
 * 9. Toast Notification Dispatcher
 * ------------------------------------------------------------------------- */
class NeoToast {
  static getContainer() {
    let container = document.querySelector('.nb-toast-container');
    if (!container) {
      container = document.createElement('div');
      container.className = 'nb-toast-container';
      document.body.appendChild(container);
    }
    return container;
  }

  /**
   * Dispatches a Neo-Brutalist toast notification.
   * @param {string} title - Heading of the alert
   * @param {string} message - Descriptive text
   * @param {'success'|'warning'|'error'|'info'} type - Color theme
   * @param {number} duration - Milliseconds before auto-dismiss
   */
  static show(title, message = '', type = 'info', duration = 4000) {
    const container = this.getContainer();

    const toast = document.createElement('div');
    toast.className = `nb-toast nb-toast-${type}`;

    let iconSymbol = 'ℹ️';
    if (type === 'success') iconSymbol = '✓';
    else if (type === 'warning') iconSymbol = '⚠';
    else if (type === 'error') iconSymbol = '✕';

    toast.innerHTML = `
      <div class="nb-toast-icon">${iconSymbol}</div>
      <div class="nb-toast-content">
        <h5 class="nb-toast-title">${title}</h5>
        ${message ? `<p class="nb-toast-message">${message}</p>` : ''}
      </div>
      <button type="button" class="nb-toast-close" aria-label="Close">×</button>
    `;

    const closeBtn = toast.querySelector('.nb-toast-close');
    closeBtn.addEventListener('click', () => this.dismiss(toast));

    container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => this.dismiss(toast), duration);
    }

    return toast;
  }

  static dismiss(toast) {
    if (!toast || !toast.parentNode) return;
    toast.style.transition = 'opacity 0.2s ease, transform 0.2s ease';
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px) scale(0.95)';
    setTimeout(() => {
      if (toast.parentNode) toast.parentNode.removeChild(toast);
    }, 200);
  }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  NeoBrutalism.init();
});

// Expose globally
window.NeoBrutalism = NeoBrutalism;
window.NeoToast = NeoToast;
