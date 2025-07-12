# ✅ ForgeVault – QA Checklist

## 🔐 Core
- [ ] Create and save encrypted password entries
- [ ] Decrypt and display securely
- [ ] Supports categories/tags or folders
- [ ] Requires master password on launch

## 💻 UI
- [ ] Minimal and distraction-free
- [ ] Passwords hidden by default
- [ ] Copy-to-clipboard works with timeout

## 🔐 Security
- [ ] AES-256 or equivalent encryption used
- [ ] Local-only storage (no cloud access)
- [ ] Proper key/IV generation
- [ ] Backup/restore support (manual)

## ⚠️ Bugs/Notes
- [ ] Input validation (no empty fields, etc.)
- [ ] Handles corrupted or missing vault file
