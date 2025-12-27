# i18n (Internationalization) Documentation

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
