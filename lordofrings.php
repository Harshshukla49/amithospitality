<?php
/**
 * Lord of the Drinks — South City Mall, Kolkata
 * Amit Hospitality LLP
 * 
 * Official brand page for Lord of the Drinks (LOTD Kolkata).
 * Upgraded with Amit AI Concierge Grounded RAG Chatbot Assistant.
 * 
 * URL Reference: https://amithospitality.com/lordofrings.php
 */
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Lord of the Drinks — South City Mall, Kolkata | Amit Hospitality</title>
  <meta name="description" content="Experience Kolkata's tallest bar and premier nightlife lounge at Lord of the Drinks, 4th Floor, South City Mall. Operated by Amit Hospitality LLP.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  
  <style>
    :root {
      --gold-primary: #f59e0b;
      --gold-light: #fbbf24;
      --gold-dark: #b45309;
      --bg-dark: #0a0b0e;
      --bg-surface: #12141a;
      --bg-surface-elevated: #1a1d26;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --border-subtle: rgba(245, 158, 11, 0.2);
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background-color: var(--bg-dark);
      color: var(--text-main);
      line-height: 1.6;
      overflow-x: hidden;
    }

    /* Top Navigation */
    header {
      background: rgba(10, 11, 14, 0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border-subtle);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 16px 40px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .brand-wrap {
      display: flex;
      align-items: center;
      gap: 14px;
      text-decoration: none;
    }

    .brand-crown {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      background: linear-gradient(135deg, var(--gold-primary), var(--gold-dark));
      display: flex;
      align-items: center;
      justify-content: center;
      color: #000;
      font-weight: 800;
      font-size: 18px;
    }

    .brand-titles h1 {
      font-family: 'Cinzel', serif;
      font-size: 18px;
      font-weight: 700;
      letter-spacing: 2px;
      color: var(--gold-light);
      text-transform: uppercase;
    }

    .brand-titles span {
      font-size: 10px;
      letter-spacing: 2.5px;
      text-transform: uppercase;
      color: var(--text-muted);
      display: block;
    }

    nav {
      display: flex;
      align-items: center;
      gap: 28px;
    }

    nav a {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      letter-spacing: 0.5px;
      transition: color 0.2s ease;
    }

    nav a:hover, nav a.active {
      color: var(--gold-light);
    }

    .btn-reserve-nav {
      padding: 8px 20px;
      border-radius: 9999px;
      background: linear-gradient(135deg, var(--gold-primary), var(--gold-dark));
      color: #000;
      font-size: 13px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 1px;
      text-decoration: none;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .btn-reserve-nav:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);
    }

    /* Hero Banner */
    .hero {
      position: relative;
      min-height: 85vh;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: 80px 24px;
      background: 
        radial-gradient(circle at 50% 30%, rgba(245, 158, 11, 0.15) 0%, transparent 60%),
        linear-gradient(180deg, rgba(10, 11, 14, 0.6) 0%, var(--bg-dark) 100%),
        url('/images/outlets/lord-of-the-drinks.webp') center/cover no-repeat;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }

    .hero-content {
      max-width: 860px;
      z-index: 10;
    }

    .hero-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 6px 18px;
      border-radius: 9999px;
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid var(--border-subtle);
      color: var(--gold-light);
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 2px;
      text-transform: uppercase;
      margin-bottom: 24px;
    }

    .hero-title {
      font-family: 'Cinzel', serif;
      font-size: clamp(34px, 5vw, 56px);
      font-weight: 800;
      line-height: 1.15;
      margin-bottom: 20px;
      text-transform: uppercase;
      background: linear-gradient(135deg, #ffffff 40%, var(--gold-light) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
      font-size: clamp(15px, 2vw, 18px);
      color: var(--text-muted);
      max-width: 680px;
      margin: 0 auto 36px;
      font-weight: 300;
    }

    .hero-cta-group {
      display: flex;
      gap: 16px;
      justify-content: center;
      flex-wrap: wrap;
    }

    .btn-gold {
      padding: 14px 32px;
      border-radius: 8px;
      background: linear-gradient(135deg, var(--gold-primary), var(--gold-dark));
      color: #000;
      font-size: 14px;
      font-weight: 700;
      letter-spacing: 1px;
      text-transform: uppercase;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      border: none;
      transition: all 0.25s ease;
    }

    .btn-gold:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 30px rgba(245, 158, 11, 0.4);
    }

    .btn-outline {
      padding: 14px 32px;
      border-radius: 8px;
      background: transparent;
      border: 1.5px solid var(--border-subtle);
      color: var(--text-main);
      font-size: 14px;
      font-weight: 600;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      transition: all 0.25s ease;
    }

    .btn-outline:hover {
      background: rgba(245, 158, 11, 0.08);
      border-color: var(--gold-primary);
      color: var(--gold-light);
    }

    /* Container & Sections */
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 80px 24px;
    }

    .section-header {
      text-align: center;
      max-width: 680px;
      margin: 0 auto 50px;
    }

    .section-tag {
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 3px;
      text-transform: uppercase;
      color: var(--gold-primary);
      margin-bottom: 8px;
      display: block;
    }

    .section-heading {
      font-family: 'Cinzel', serif;
      font-size: 32px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 14px;
    }

    .section-desc {
      color: var(--text-muted);
      font-size: 15px;
    }

    /* Highlights Grid */
    .features-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 24px;
      margin-bottom: 60px;
    }

    .feature-card {
      background: var(--bg-surface);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 14px;
      padding: 32px 24px;
      transition: all 0.25s ease;
      position: relative;
    }

    .feature-card:hover {
      transform: translateY(-4px);
      border-color: var(--border-subtle);
      box-shadow: 0 12px 36px rgba(0, 0, 0, 0.4);
    }

    .feature-icon {
      font-size: 28px;
      margin-bottom: 16px;
    }

    .feature-title {
      font-family: 'Cinzel', serif;
      font-size: 18px;
      color: #fff;
      margin-bottom: 10px;
      font-weight: 700;
    }

    .feature-text {
      color: var(--text-muted);
      font-size: 14px;
      line-height: 1.6;
    }

    /* Signature Menu Teaser */
    .menu-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 24px;
    }

    .menu-card {
      background: var(--bg-surface);
      border: 1px solid rgba(255, 255, 255, 0.06);
      border-radius: 12px;
      padding: 24px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      transition: border-color 0.2s ease;
    }

    .menu-card:hover {
      border-color: var(--border-subtle);
    }

    .menu-info h4 {
      font-size: 16px;
      color: #fff;
      font-weight: 600;
      margin-bottom: 6px;
    }

    .menu-info p {
      font-size: 13px;
      color: var(--text-muted);
      line-height: 1.5;
    }

    .menu-price {
      font-family: 'Cinzel', serif;
      font-size: 16px;
      color: var(--gold-light);
      font-weight: 700;
      white-space: nowrap;
    }

    /* Venue Info Banner */
    .venue-strip {
      background: var(--bg-surface-elevated);
      border-radius: 16px;
      border: 1px solid var(--border-subtle);
      padding: 40px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 32px;
      margin-top: 60px;
    }

    .strip-item h5 {
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 2px;
      color: var(--gold-primary);
      margin-bottom: 8px;
    }

    .strip-item p {
      font-size: 14px;
      color: #e2e8f0;
    }

    /* Footer */
    footer {
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      background: #07080a;
      padding: 60px 40px 30px;
      font-size: 13px;
      color: var(--text-muted);
    }

    .footer-content {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 40px;
      margin-bottom: 40px;
    }

    .footer-col h4 {
      color: #fff;
      font-size: 14px;
      margin-bottom: 16px;
      text-transform: uppercase;
      letter-spacing: 1px;
    }

    .footer-col ul {
      list-style: none;
    }

    .footer-col ul li {
      margin-bottom: 8px;
    }

    .footer-col ul li a {
      color: var(--text-muted);
      text-decoration: none;
      transition: color 0.2s;
    }

    .footer-col ul li a:hover {
      color: var(--gold-light);
    }

    .footer-bottom {
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      padding-top: 24px;
      text-align: center;
      max-width: 1200px;
      margin: 0 auto;
    }
  </style>
</head>
<body>

  <!-- Header -->
  <header>
    <a href="/" class="brand-wrap">
      <div class="brand-crown">👑</div>
      <div class="brand-titles">
        <h1>Lord of the Drinks</h1>
        <span>Amit Hospitality • Kolkata</span>
      </div>
    </a>
    <nav>
      <a href="#about" class="active">Venue</a>
      <a href="#mixology">Mixology</a>
      <a href="#menu">Cuisine</a>
      <a href="#location">South City Mall</a>
      <a href="https://concierge.amithospitality.com/?outlet=lord-of-the-drinks" class="btn-reserve-nav">Reserve Table</a>
    </nav>
  </header>

  <!-- Hero Section -->
  <section class="hero">
    <div class="hero-content">
      <div class="hero-pill">✨ Kolkata's Tallest Bar &amp; Ghost Bar</div>
      <h2 class="hero-title">Experience Medieval Royalty at Lord of the Drinks</h2>
      <p class="hero-subtitle">
        Perched on the 4th Floor of South City Mall, Prince Anwar Shah Road. 
        Kolkata's most celebrated experiential nightlife and dining sanctuary by Amit Hospitality LLP.
      </p>
      <div class="hero-cta-group">
        <a href="#menu" class="btn-gold">Explore Signature Menus</a>
        <a href="https://concierge.amithospitality.com/?outlet=lord-of-the-drinks" class="btn-outline">Open Concierge Portal</a>
      </div>
    </div>
  </section>

  <!-- Curated Highlights -->
  <main class="container" id="about">
    <div class="section-header">
      <span class="section-tag">Grandeur &amp; Craft</span>
      <h3 class="section-heading">Why Lord of the Drinks Defines Kolkata Nightlife</h3>
      <p class="section-desc">Sprawling over 4,000+ square feet with soaring ceilings, custom wrought-iron decor, and Kolkata's most innovative cocktail laboratory.</p>
    </div>

    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">🍸</div>
        <div class="feature-title">Kolkata's Tallest Bar</div>
        <div class="feature-text">
          An architectural marvel housing single malts, botanical gins, and progressive mixology including <em>My 18th Birthday</em> and <em>Lavender Sour</em>.
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🏰</div>
        <div class="feature-title">The Ghost Bar &amp; Cabanas</div>
        <div class="feature-text">
          Subterranean medieval lighting, VIP private cabanas for celebrations, and high-energy weekend DJ sets curated for up to 220 guests.
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🥢</div>
        <div class="feature-title">Global Multi-Cuisine</div>
        <div class="feature-text">
          Progressive Continental, Modern North Indian, and Pan-Asian small plates. Strict kitchen segregation and pure Jain menus available.
        </div>
      </div>
      <div class="feature-card">
        <div class="feature-icon">🅿️</div>
        <div class="feature-title">South City Valet &amp; Access</div>
        <div class="feature-text">
          Direct express elevator access from South City Mall main atrium. 1,500+ covered multi-level basement parking with porch valet drop-off.
        </div>
      </div>
    </div>

    <!-- Signature Menu Section -->
    <div class="section-header" id="mixology" style="margin-top: 80px;">
      <span class="section-tag">Chef &amp; Mixologist Signatures</span>
      <h3 class="section-heading">Crafted Cocktails &amp; Artisanal Plates</h3>
      <p class="section-desc">Sample our most celebrated creations, prepared fresh daily by executive culinary teams.</p>
    </div>

    <div class="menu-grid" id="menu">
      <div class="menu-card">
        <div class="menu-info">
          <h4>My 18th Birthday</h4>
          <p>Vodka, rich butterscotch liqueur, salted caramel, popcorn syrup, and fresh pineapple juice.</p>
        </div>
        <div class="menu-price">₹675</div>
      </div>
      <div class="menu-card">
        <div class="menu-info">
          <h4>Lavender Sour</h4>
          <p>Botanical gin, organic lavender blossom tincture, butterfly pea flower tea, fresh lime, vegan aquafaba.</p>
        </div>
        <div class="menu-price">₹695</div>
      </div>
      <div class="menu-card">
        <div class="menu-info">
          <h4>Mustard Crusted Bhetki Tikka</h4>
          <p>Fresh Bengal bhetki fillets marinated in stone-ground Kasundi mustard and yellow chili, clay-oven roasted.</p>
        </div>
        <div class="menu-price">₹795</div>
      </div>
      <div class="menu-card">
        <div class="menu-info">
          <h4>Truffle &amp; Edamame Dimsums</h4>
          <p>Hand-rolled translucent dumplings with crushed edamame, water chestnuts, and white truffle essence.</p>
        </div>
        <div class="menu-price">₹595</div>
      </div>
      <div class="menu-card">
        <div class="menu-info">
          <h4>Slow-Cooked 24-Hr Dal Makhani</h4>
          <p>Simmered overnight over glowing coals, finished with hand-churned truffle butter and cream.</p>
        </div>
        <div class="menu-price">₹525</div>
      </div>
      <div class="menu-card">
        <div class="menu-info">
          <h4>Classic Dark Chocolate Sphere</h4>
          <p>Belgian dark chocolate dome with hazelnut praline mousse, poured over with hot salted caramel ganache.</p>
        </div>
        <div class="menu-price">₹475</div>
      </div>
    </div>

    <!-- Venue Strip Details -->
    <div class="venue-strip" id="location">
      <div class="strip-item">
        <h5>Operating Hours</h5>
        <p>12:00 PM – 12:00 AM<br>Every day (Lunch &amp; Evening Lounge)</p>
      </div>
      <div class="strip-item">
        <h5>Location</h5>
        <p>4th Floor, South City Mall<br>Prince Anwar Shah Rd, Jadavpur, Kolkata</p>
      </div>
      <div class="strip-item">
        <h5>Dress Code</h5>
        <p>Smart Casual (Closed shoes &amp; collared shirts; no flip-flops after 7 PM)</p>
      </div>
      <div class="strip-item">
        <h5>Age Policy</h5>
        <p>Family lunch welcome.<br>Strictly 21+ with photo ID after 7:00 PM</p>
      </div>
    </div>
  </main>

  <!-- Footer -->
  <footer>
    <div class="footer-content">
      <div class="footer-col" style="max-width: 380px;">
        <h4 style="color: var(--gold-light);">Lord of the Drinks Kolkata</h4>
        <p style="margin-bottom: 12px;">Operated by Amit Hospitality LLP (Amit &amp; Vanita Bajoria). Curating India's most extraordinary culinary and nightlife destinations.</p>
        <p><strong>Registered Office:</strong> 401 Kamalalaya Centre, 156A Lenin Sarani, Kolkata - 700013.</p>
      </div>
      <div class="footer-col">
        <h4>Our Brand Portfolio</h4>
        <ul>
          <li><a href="/lordofrings.php">Lord of the Drinks</a></li>
          <li><a href="#">Veneto Kitchen &amp; Bar</a></li>
          <li><a href="#">The Warehouse Cafe</a></li>
          <li><a href="#">Deliite</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Concierge Desk</h4>
        <ul>
          <li>Phone: +91 11 4050 9900</li>
          <li>Email: concierge@amithospitality.com</li>
          <li>South City Mall Desk: Ext. 401</li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      © 2026 Amit Hospitality LLP • All rights reserved. Powered by Amit AI Concierge.
    </div>
  </footer>

  <!-- ========================================================================= -->
  <!-- STEP 1 & STEP 2: AMIT AI CONCIERGE DROP-IN FLOATING CHAT WIDGET           -->
  <!-- ========================================================================= -->
  <script 
    src="https://concierge.amithospitality.com/widget.js" 
    data-outlet="lord-of-the-drinks" 
    data-accent-color="#F59E0B" 
    data-position="bottom-right">
  </script>

  <!-- Local development smart resolver: seamlessly uses local widget when running on localhost -->
  <script>
    (function() {
      if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        var existingScript = document.querySelector('script[src*="widget.js"]');
        if (existingScript && existingScript.src.includes('concierge.amithospitality.com')) {
          existingScript.src = window.location.origin + '/widget.js';
        }
      }
    })();
  </script>

</body>
</html>
