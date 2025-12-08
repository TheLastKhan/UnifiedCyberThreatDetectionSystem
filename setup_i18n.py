"""
Frontend i18n (Internationalization) Setup
=============================================

Sets up Turkish-English localization for web dashboard.

Features:
- Language switching (Türkçe ↔ English)
- Persistent language preference (localStorage)
- Professional translations
- RTL support ready (for future languages)
- Translation key consistency checks

Directory Structure:
web_dashboard/
├── static/
│   └── i18n/
│       ├── en.json          (English translations)
│       ├── tr.json          (Turkish translations)
│       └── languages.json   (Language metadata)
└── templates/
    └── dashboard.html       (HTML with i18n keys)

Installation:
1. npm install i18next i18next-browser-languagedetector
2. npm install i18next-http-backend
3. Include in HTML: <script src="static/i18n/i18next.min.js"></script>
"""

import json
from pathlib import Path
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Translation keys mapping
UI_TRANSLATIONS = {
    # Header
    "header.title": {
        "en": "Unified Cyber Threat Detection System",
        "tr": "Birleşik Siber Tehdit Algılama Sistemi"
    },
    "header.subtitle": {
        "en": "Real-time Email & Web Threat Analysis",
        "tr": "Gerçek Zamanlı E-posta ve Web Tehdit Analizi"
    },
    
    # Navigation
    "nav.dashboard": {
        "en": "Dashboard",
        "tr": "Kontrol Paneli"
    },
    "nav.analysis": {
        "en": "Analysis",
        "tr": "Analiz"
    },
    "nav.threats": {
        "en": "Threats",
        "tr": "Tehditler"
    },
    "nav.reports": {
        "en": "Reports",
        "tr": "Raporlar"
    },
    "nav.settings": {
        "en": "Settings",
        "tr": "Ayarlar"
    },
    
    # Email Analysis
    "email.title": {
        "en": "Email Analysis",
        "tr": "E-posta Analizi"
    },
    "email.upload": {
        "en": "Upload Email",
        "tr": "E-posta Yükle"
    },
    "email.sender": {
        "en": "Sender",
        "tr": "Gönderici"
    },
    "email.subject": {
        "en": "Subject",
        "tr": "Konu"
    },
    "email.body": {
        "en": "Message Body",
        "tr": "İleti Metni"
    },
    "email.analyze": {
        "en": "Analyze Email",
        "tr": "E-postayı Analiz Et"
    },
    "email.phishing": {
        "en": "Phishing Detection",
        "tr": "Kimlik Avı Algılaması"
    },
    "email.spam": {
        "en": "Spam Detection",
        "tr": "Spam Algılaması"
    },
    
    # Web Analysis
    "web.title": {
        "en": "Web Log Analysis",
        "tr": "Web Günlüğü Analizi"
    },
    "web.upload": {
        "en": "Upload Logs",
        "tr": "Günlükleri Yükle"
    },
    "web.url": {
        "en": "URL",
        "tr": "URL"
    },
    "web.method": {
        "en": "HTTP Method",
        "tr": "HTTP Yöntemi"
    },
    "web.status": {
        "en": "Status Code",
        "tr": "Durum Kodu"
    },
    "web.analyze": {
        "en": "Analyze Logs",
        "tr": "Günlükleri Analiz Et"
    },
    
    # Risk Levels
    "risk.critical": {
        "en": "CRITICAL",
        "tr": "KRİTİK"
    },
    "risk.high": {
        "en": "HIGH",
        "tr": "YÜKSEK"
    },
    "risk.medium": {
        "en": "MEDIUM",
        "tr": "ORTA"
    },
    "risk.low": {
        "en": "LOW",
        "tr": "DÜŞÜK"
    },
    
    # Threat Types
    "threat.phishing": {
        "en": "Phishing",
        "tr": "Kimlik Avı"
    },
    "threat.malware": {
        "en": "Malware",
        "tr": "Kötü Amaçlı Yazılım"
    },
    "threat.spam": {
        "en": "Spam",
        "tr": "İstenmeyen Posta"
    },
    "threat.injection": {
        "en": "SQL Injection",
        "tr": "SQL Enjeksiyonu"
    },
    "threat.xss": {
        "en": "Cross-Site Scripting",
        "tr": "Siteler Arası Komut Dosyası"
    },
    "threat.ddos": {
        "en": "DDoS Attack",
        "tr": "DDoS Saldırısı"
    },
    
    # Statistics
    "stats.total_emails": {
        "en": "Total Emails",
        "tr": "Toplam E-postalar"
    },
    "stats.threats_detected": {
        "en": "Threats Detected",
        "tr": "Algılanan Tehditler"
    },
    "stats.success_rate": {
        "en": "Detection Rate",
        "tr": "Algılama Oranı"
    },
    "stats.avg_score": {
        "en": "Avg. Risk Score",
        "tr": "Ort. Risk Puanı"
    },
    
    # Buttons
    "button.submit": {
        "en": "Submit",
        "tr": "Gönder"
    },
    "button.cancel": {
        "en": "Cancel",
        "tr": "İptal"
    },
    "button.save": {
        "en": "Save",
        "tr": "Kaydet"
    },
    "button.delete": {
        "en": "Delete",
        "tr": "Sil"
    },
    "button.export": {
        "en": "Export",
        "tr": "Dışa Aktar"
    },
    "button.refresh": {
        "en": "Refresh",
        "tr": "Yenile"
    },
    
    # Messages
    "msg.success": {
        "en": "Operation successful!",
        "tr": "İşlem başarıyla tamamlandı!"
    },
    "msg.error": {
        "en": "An error occurred. Please try again.",
        "tr": "Bir hata oluştu. Lütfen tekrar deneyin."
    },
    "msg.loading": {
        "en": "Loading...",
        "tr": "Yükleniyor..."
    },
    "msg.no_data": {
        "en": "No data available",
        "tr": "Veri yok"
    },
    
    # Settings
    "settings.theme": {
        "en": "Theme",
        "tr": "Tema"
    },
    "settings.dark_mode": {
        "en": "Dark Mode",
        "tr": "Koyu Mod"
    },
    "settings.light_mode": {
        "en": "Light Mode",
        "tr": "Açık Mod"
    },
    "settings.language": {
        "en": "Language",
        "tr": "Dil"
    },
    "settings.notifications": {
        "en": "Notifications",
        "tr": "Bildirimler"
    },
}

# Language metadata
LANGUAGE_METADATA = {
    "en": {
        "name": "English",
        "native": "English",
        "direction": "ltr",
        "code": "en"
    },
    "tr": {
        "name": "Turkish",
        "native": "Türkçe",
        "direction": "ltr",
        "code": "tr"
    }
}


def create_translation_files():
    """Create i18n translation files"""
    logger.info("Creating translation files...")
    
    i18n_dir = Path("web_dashboard/static/i18n")
    i18n_dir.mkdir(parents=True, exist_ok=True)
    
    # Separate translations by language
    translations = {"en": {}, "tr": {}}
    
    for key, values in UI_TRANSLATIONS.items():
        for lang, text in values.items():
            translations[lang][key] = text
    
    # Save translation files
    for lang, translation_dict in translations.items():
        file_path = i18n_dir / f"{lang}.json"
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(translation_dict, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Created {file_path} ({len(translation_dict)} keys)")
    
    # Save language metadata
    metadata_path = i18n_dir / "languages.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(LANGUAGE_METADATA, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✅ Created {metadata_path}")
    
    return i18n_dir


def create_i18n_config():
    """Create i18next configuration"""
    logger.info("Creating i18next configuration...")
    
    config = {
        "lng": "en",  # Default language
        "fallbackLng": "en",
        "ns": ["translation"],
        "defaultNS": "translation",
        "debug": False,
        "interpolation": {
            "escapeValue": False  # React already escapes by default
        },
        "resources": {}
    }
    
    # Load translations into config
    i18n_dir = Path("web_dashboard/static/i18n")
    
    for lang_file in i18n_dir.glob("*.json"):
        if lang_file.name == "languages.json":
            continue
        
        lang_code = lang_file.stem
        
        with open(lang_file, "r", encoding="utf-8") as f:
            translations = json.load(f)
        
        config["resources"][lang_code] = {
            "translation": translations
        }
    
    config_path = Path("web_dashboard/static/i18n/i18next.config.js")
    
    # JavaScript config format
    js_config = f"""// i18next configuration
const i18nextConfig = {json.dumps(config, indent=2, ensure_ascii=False)};

export default i18nextConfig;
"""
    
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(js_config)
    
    logger.info(f"✅ Created {config_path}")


def create_i18n_initializer():
    """Create i18next initializer script"""
    logger.info("Creating i18next initializer script...")
    
    initializer_code = '''// i18n initialization script
// Include this in your main dashboard HTML

<script src="https://cdn.jsdelivr.net/npm/i18next@23.7.6/dist/umd/i18next.min.js"></script>
<script>
    // Initialize i18next
    i18next
        .init({
            lng: localStorage.getItem('language') || 'en',
            fallbackLng: 'en',
            debug: false,
            resources: {
                en: {
                    translation: {}
                },
                tr: {
                    translation: {}
                }
            }
        })
        .then(() => {
            console.log('✅ i18next initialized');
            updatePageLanguage();
        })
        .catch(err => {
            console.error('❌ i18next initialization failed:', err);
        });

    // Update all elements with data-i18n attribute
    function updatePageLanguage() {
        document.querySelectorAll('[data-i18n]').forEach(el => {
            const key = el.getAttribute('data-i18n');
            el.textContent = i18next.t(key);
        });
    }

    // Language switcher
    function setLanguage(lang) {
        i18next.changeLanguage(lang, () => {
            localStorage.setItem('language', lang);
            updatePageLanguage();
            console.log(`Language changed to: ${lang}`);
        });
    }

    // Listen to language changes
    i18next.on('languageChanged', () => {
        updatePageLanguage();
    });
</script>

<!-- Language Switcher Button -->
<div class="language-switcher">
    <button onclick="setLanguage('en')">English</button>
    <button onclick="setLanguage('tr')">Türkçe</button>
</div>

<!-- Usage Example -->
<!-- Instead of: <h1>Dashboard</h1> -->
<!-- Use: <h1 data-i18n="header.title"></h1> -->
'''
    
    init_path = Path("web_dashboard/static/i18n/i18next-init.html")
    
    with open(init_path, "w", encoding="utf-8") as f:
        f.write(initializer_code)
    
    logger.info(f"✅ Created {init_path}")


def create_css_i18n():
    """Create CSS with i18n support (for RTL future)"""
    logger.info("Creating i18n-aware CSS...")
    
    css_content = '''/* i18n CSS Support */

:root {
    /* Default (LTR) CSS Custom Properties */
    --dir: ltr;
    --text-align-start: left;
    --text-align-end: right;
    --float-start: left;
    --float-end: right;
    --margin-start: margin-left;
    --margin-end: margin-right;
    --padding-start: padding-left;
    --padding-end: padding-right;
    --border-start: border-left;
    --border-end: border-right;
}

/* RTL Support (when needed for future languages) */
html[lang="ar"],
html[lang="he"],
html[lang="fa"] {
    --dir: rtl;
    --text-align-start: right;
    --text-align-end: left;
    --float-start: right;
    --float-end: left;
    --margin-start: margin-right;
    --margin-end: margin-left;
    --padding-start: padding-right;
    --padding-end: padding-left;
    --border-start: border-right;
    --border-end: border-left;
}

/* Language-specific font stacks */
body[lang="tr"],
body[lang="en"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* Component styling */
.language-switcher {
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 1000;
    display: flex;
    gap: 10px;
}

.language-switcher button {
    padding: 8px 12px;
    border: 1px solid #ccc;
    border-radius: 4px;
    background: white;
    cursor: pointer;
    font-size: 12px;
    font-weight: 500;
}

.language-switcher button:hover {
    background: #f0f0f0;
    border-color: #999;
}

.language-switcher button.active {
    background: #007bff;
    color: white;
    border-color: #0056b3;
}

/* Text directionality */
.text-start {
    text-align: var(--text-align-start);
}

.text-end {
    text-align: var(--text-align-end);
}

/* Margin shortcuts */
.ms-auto {
    margin-inline-start: auto;
}

.me-auto {
    margin-inline-end: auto;
}

/* Padding shortcuts */
.ps-2 {
    padding-inline-start: 0.5rem;
}

.pe-2 {
    padding-inline-end: 0.5rem;
}
'''
    
    css_path = Path("web_dashboard/static/css/i18n.css")
    css_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css_content)
    
    logger.info(f"✅ Created {css_path}")


def create_html_template():
    """Create HTML template with i18n markers"""
    logger.info("Creating HTML template with i18n support...")
    
    html_template = '''<!-- HTML Template with i18n Support -->

<!-- Include i18n CSS -->
<link rel="stylesheet" href="static/css/i18n.css">

<!-- Header with i18n -->
<header>
    <h1 data-i18n="header.title"></h1>
    <p data-i18n="header.subtitle"></p>
</header>

<!-- Navigation -->
<nav>
    <ul>
        <li><a href="#" data-i18n="nav.dashboard"></a></li>
        <li><a href="#" data-i18n="nav.analysis"></a></li>
        <li><a href="#" data-i18n="nav.threats"></a></li>
        <li><a href="#" data-i18n="nav.reports"></a></li>
        <li><a href="#" data-i18n="nav.settings"></a></li>
    </ul>
</nav>

<!-- Email Analysis Section -->
<section id="email-analysis">
    <h2 data-i18n="email.title"></h2>
    <form>
        <label data-i18n="email.sender"></label>
        <input type="email" placeholder="sender@example.com">
        
        <label data-i18n="email.subject"></label>
        <input type="text" placeholder="">
        
        <label data-i18n="email.body"></label>
        <textarea></textarea>
        
        <button type="submit" data-i18n="email.analyze"></button>
    </form>
</section>

<!-- Web Analysis Section -->
<section id="web-analysis">
    <h2 data-i18n="web.title"></h2>
    <form>
        <label data-i18n="web.url"></label>
        <input type="url" placeholder="https://example.com">
        
        <button type="submit" data-i18n="web.analyze"></button>
    </form>
</section>

<!-- Risk Level Display -->
<div class="risk-indicator">
    <div class="risk critical">
        <span data-i18n="risk.critical"></span>
    </div>
    <div class="risk high">
        <span data-i18n="risk.high"></span>
    </div>
    <div class="risk medium">
        <span data-i18n="risk.medium"></span>
    </div>
    <div class="risk low">
        <span data-i18n="risk.low"></span>
    </div>
</div>

<!-- Settings -->
<section id="settings">
    <h2 data-i18n="nav.settings"></h2>
    
    <div class="setting-group">
        <label data-i18n="settings.theme"></label>
        <button id="dark-mode-toggle">
            <span data-i18n="settings.dark_mode"></span>
        </button>
    </div>
    
    <div class="setting-group">
        <label data-i18n="settings.language"></label>
        <select id="language-select">
            <option value="en">English</option>
            <option value="tr">Türkçe</option>
        </select>
    </div>
</section>

<!-- Include i18next initialization -->
<script src="static/i18n/i18next-init.html"></script>

<!-- Language change listener -->
<script>
    document.getElementById('language-select')?.addEventListener('change', (e) => {
        setLanguage(e.target.value);
    });
</script>
'''
    
    template_path = Path("web_dashboard/templates/i18n-template.html")
    template_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(html_template)
    
    logger.info(f"✅ Created {template_path}")


def create_documentation():
    """Create i18n documentation"""
    logger.info("Creating documentation...")
    
    doc_content = """# i18n (Internationalization) Documentation

## Overview

This project supports Turkish (Türkçe) and English for the web dashboard.

## Setup

1. **Include i18next library**:
   ```html
   <script src="https://cdn.jsdelivr.net/npm/i18next@23.7.6/dist/umd/i18next.min.js"></script>
   ```

2. **Load translations**:
   - English: `static/i18n/en.json`
   - Turkish: `static/i18n/tr.json`

3. **Initialize i18next**:
   ```javascript
   i18next.init({
       lng: localStorage.getItem('language') || 'en',
       fallbackLng: 'en',
       resources: { /* translations */ }
   });
   ```

## Usage

### In HTML

Use `data-i18n` attribute:

```html
<h1 data-i18n="header.title"></h1>
<button data-i18n="button.submit"></button>
```

### In JavaScript

```javascript
const text = i18next.t('email.subject');
console.log(text); // "Subject" or "Konu"
```

### Language Switching

```javascript
function setLanguage(lang) {
    i18next.changeLanguage(lang, () => {
        localStorage.setItem('language', lang);
        updatePageLanguage();
    });
}
```

## Adding New Translations

1. Edit `static/i18n/en.json` and `static/i18n/tr.json`
2. Add key-value pairs:
   ```json
   {
       "myfeature.title": "My Feature"
   }
   ```
3. Use in HTML with `data-i18n="myfeature.title"`

## Translation Keys

All keys follow the pattern: `section.key`

### Sections:
- `header.*` - Header elements
- `nav.*` - Navigation
- `email.*` - Email analysis
- `web.*` - Web analysis
- `risk.*` - Risk levels
- `threat.*` - Threat types
- `stats.*` - Statistics
- `button.*` - Buttons
- `msg.*` - Messages
- `settings.*` - Settings

## Language Persistence

Language preference is saved to localStorage:
- Key: `language`
- Values: `en` or `tr`

On page load, the saved language is automatically applied.

## RTL Support (Future)

The CSS includes RTL support for future languages (Arabic, Hebrew, Persian):

```css
html[lang="ar"],
html[lang="he"],
html[lang="fa"] {
    --dir: rtl;
    /* ... */
}
```

## Troubleshooting

### Translations not appearing?
1. Check browser console for errors
2. Verify JSON files are valid
3. Check that `data-i18n` keys match JSON keys

### Language not persisting?
1. Check localStorage is enabled
2. Verify `setLanguage()` is called
3. Check browser privacy settings

## Best Practices

1. **Key naming**: Use descriptive, hierarchical keys
2. **Consistency**: Keep terminology consistent across translations
3. **Context**: Provide context in comments for translators
4. **Formatting**: Keep JSON files clean and organized
5. **Testing**: Test both languages before deployment

## Files

```
web_dashboard/
├── static/
│   ├── i18n/
│   │   ├── en.json                (English translations)
│   │   ├── tr.json                (Turkish translations)
│   │   ├── languages.json         (Language metadata)
│   │   ├── i18next.config.js      (i18next configuration)
│   │   └── i18next-init.html      (Initialization script)
│   └── css/
│       └── i18n.css               (i18n-aware styling)
└── templates/
    ├── dashboard.html              (Main dashboard)
    └── i18n-template.html          (i18n template reference)
```

## References

- [i18next Documentation](https://www.i18next.com/)
- [i18next GitHub](https://github.com/i18next/i18next)
- [Internationalization Best Practices](https://www.w3.org/International/questions/qa-what-is-i18n)
"""
    
    doc_path = Path("web_dashboard/static/i18n/I18N_README.md")
    
    with open(doc_path, "w", encoding="utf-8") as f:
        f.write(doc_content)
    
    logger.info(f"✅ Created {doc_path}")


def setup_i18n():
    """Complete i18n setup"""
    logger.info("="*60)
    logger.info("FRONTEND i18n SETUP - ENGLISH & TURKISH")
    logger.info("="*60)
    
    create_translation_files()
    create_i18n_config()
    create_i18n_initializer()
    create_css_i18n()
    create_html_template()
    create_documentation()
    
    logger.info("\n" + "="*60)
    logger.info("✅ i18n SETUP COMPLETED!")
    logger.info("="*60)
    
    logger.info("\nNext steps:")
    logger.info("1. Include i18next library in dashboard.html")
    logger.info("2. Add data-i18n attributes to HTML elements")
    logger.info("3. Include i18n initialization script")
    logger.info("4. Test language switching")
    logger.info("\nSee: web_dashboard/static/i18n/I18N_README.md")


if __name__ == "__main__":
    setup_i18n()
