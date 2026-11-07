/**
 * Amit AI Concierge — Embeddable Luxury Chat Widget
 * Official deployment script for https://amithospitality.com/
 * 
 * Usage:
 * <script src="https://concierge.amithospitality.com/widget.js" 
 *         data-outlet="amber-terrace" 
 *         data-accent-color="#D4AF37" 
 *         data-position="bottom-right"></script>
 */

(function () {
  'use strict';

  // Read configuration from script tag attributes
  var scriptTag = document.currentScript || (function () {
    var scripts = document.getElementsByTagName('script');
    return scripts[scripts.length - 1];
  })();

  var defaultOutlet = scriptTag ? scriptTag.getAttribute('data-outlet') || 'amber-terrace' : 'amber-terrace';
  var accentColor = scriptTag ? scriptTag.getAttribute('data-accent-color') || '#D4AF37' : '#D4AF37';
  var position = scriptTag ? scriptTag.getAttribute('data-position') || 'bottom-right' : 'bottom-right';

  // Base URL calculation
  var scriptSrc = scriptTag ? scriptTag.src : window.location.href;
  var baseUrl = scriptSrc.substring(0, scriptSrc.lastIndexOf('/'));
  var conciergeUrl = baseUrl.replace('/public', '') + '/?outlet=' + encodeURIComponent(defaultOutlet) + '&embed=true';

  // Inject Styles
  var style = document.createElement('style');
  style.innerHTML = `
    #amit-concierge-launcher {
      position: fixed;
      ${position.includes('left') ? 'left: 24px;' : 'right: 24px;'}
      bottom: 24px;
      z-index: 999998;
      width: 58px;
      height: 58px;
      border-radius: 50%;
      background: linear-gradient(135deg, #18191B 0%, #0F0F11 100%);
      border: 1.5px solid ${accentColor};
      box-shadow: 0 8px 32px rgba(212, 175, 55, 0.28), 0 4px 12px rgba(0,0,0,0.5);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    }
    #amit-concierge-launcher:hover {
      transform: scale(1.08) translateY(-2px);
      box-shadow: 0 12px 40px rgba(212, 175, 55, 0.45);
    }
    #amit-concierge-launcher svg {
      width: 26px;
      height: 26px;
      fill: none;
      stroke: ${accentColor};
      stroke-width: 2;
      stroke-linecap: round;
      stroke-linejoin: round;
      transition: transform 0.25s ease;
    }
    #amit-concierge-frame-container {
      position: fixed;
      ${position.includes('left') ? 'left: 24px;' : 'right: 24px;'}
      bottom: 96px;
      width: 420px;
      max-width: calc(100vw - 32px);
      height: 640px;
      max-height: calc(100vh - 120px);
      z-index: 999999;
      border-radius: 20px;
      overflow: hidden;
      border: 1.5px solid rgba(212, 175, 55, 0.35);
      box-shadow: 0 20px 60px rgba(0,0,0,0.8), 0 0 40px rgba(212, 175, 55, 0.15);
      background: #0A0A0C;
      display: none;
      opacity: 0;
      transform: translateY(16px) scale(0.96);
      transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }
    #amit-concierge-frame-container.open {
      display: block;
      opacity: 1;
      transform: translateY(0) scale(1);
    }
    #amit-concierge-iframe {
      width: 100%;
      height: 100%;
      border: none;
    }
    @media (max-width: 480px) {
      #amit-concierge-frame-container {
        bottom: 0;
        right: 0;
        left: 0;
        width: 100vw;
        max-width: 100vw;
        height: 100vh;
        max-height: 100vh;
        border-radius: 0;
        border: none;
      }
      #amit-concierge-launcher {
        bottom: 16px;
        right: 16px;
      }
    }
  `;
  document.head.appendChild(style);

  // Create Launcher Button
  var launcher = document.createElement('div');
  launcher.id = 'amit-concierge-launcher';
  launcher.title = 'Converse with Amit AI Concierge';
  launcher.innerHTML = `
    <svg id="amit-icon-open" viewBox="0 0 24 24">
      <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"></path>
    </svg>
    <svg id="amit-icon-close" style="display:none;" viewBox="0 0 24 24">
      <line x1="18" y1="6" x2="6" y2="18"></line>
      <line x1="6" y1="6" x2="18" y2="18"></line>
    </svg>
  `;

  // Create Popup Container with Iframe
  var container = document.createElement('div');
  container.id = 'amit-concierge-frame-container';
  var iframe = document.createElement('iframe');
  iframe.id = 'amit-concierge-iframe';
  iframe.src = conciergeUrl;
  iframe.setAttribute('allow', 'microphone; clipboard-write');
  container.appendChild(iframe);

  document.body.appendChild(launcher);
  document.body.appendChild(container);

  var isOpen = false;

  launcher.addEventListener('click', function () {
    isOpen = !isOpen;
    if (isOpen) {
      container.classList.add('open');
      document.getElementById('amit-icon-open').style.display = 'none';
      document.getElementById('amit-icon-close').style.display = 'block';
    } else {
      container.classList.remove('open');
      document.getElementById('amit-icon-open').style.display = 'block';
      document.getElementById('amit-icon-close').style.display = 'none';
    }
  });

  // Listen to messages from child iframe (e.g. close requests)
  window.addEventListener('message', function (e) {
    if (e.data === 'amit-close-widget') {
      isOpen = false;
      container.classList.remove('open');
      document.getElementById('amit-icon-open').style.display = 'block';
      document.getElementById('amit-icon-close').style.display = 'none';
    }
  });

  console.log('[Amit AI Concierge] Luxury Widget initialized for:', defaultOutlet);
})();
