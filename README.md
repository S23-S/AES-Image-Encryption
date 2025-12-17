# AES Image Encryption

This project demonstrates how different AES encryption modes affect image security.  
It focuses on the **ECB image attack**, where image patterns remain visible after encryption, and compares it with more secure modes such as **CBC** and **CTR**.

## 🔐 Encryption Modes Implemented

- **AES-ECB** (Insecure – for educational purposes only)
- **AES-CBC** (Secure with random IV)
- **AES-CTR** (Secure stream-based encryption)

## 🖼️ ECB Image Attack

AES-ECB encrypts identical plaintext blocks into identical ciphertext blocks.  
When applied to images, this causes:
- Visible outlines
- Leaked shapes and structures
- Broken confidentiality

This repository visually and programmatically demonstrates why **ECB must never be used for images or structured data**.

## ✅ Secure Alternatives

- **CBC Mode**: Uses chaining and a random IV to remove patterns
- **CTR Mode**: Uses a counter-based keystream to encrypt each block uniquely

Both modes successfully eliminate visible image patterns.

## 🧪 Technologies Used

- Python 3
- PyCryptodome (`Crypto.Cipher.AES`)
- Secure random key and IV/nonce generation

## ⚠️ Security Notice

ECB mode is included **only for learning and demonstration purposes**.  
For real-world applications, use **AES-GCM**, **AES-CBC**, or **AES-CTR** with proper key and IV/nonce management.

## 🎯 Educational Purpose

This project is intended for:
- Cryptography learning
- Security demonstrations
- University coursework
- Understanding why encryption mode selection matters

---

**Author:** S23-S  
**License:** MIT
