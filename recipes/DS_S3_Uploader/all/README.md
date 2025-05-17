# DS-S3-Uploader

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20MacOS-brightgreen.svg)
![Language](https://img.shields.io/badge/language-C++17-blue.svg)

`DS-S3-Uploader` is a lightweight and easy-to-use C++ library for uploading files to any S3-compatible object storage, such as **ArvanCloud**, **MinIO**, or **Amazon S3**, using HTTP PUT requests.

---

## ✨ Features

- ✅ Compatible with any S3-compatible storage (AWS, ArvanCloud, MinIO, etc.)
- 📦 Header-only / static / shared library support
- 🔐 Supports custom endpoint & access credentials
- ⚡ Fast and minimal dependency (uses `cpr` and `OpenSSL`)
- 🧪 Tested and designed for modern C++ projects

---

## 📦 Installing via Conan

Make sure you are using **Conan 2.x**.

### 1. Add remote (if private or hosted somewhere)

If the library is public on GitHub:

```bash
conan remote add ds_s3_uploader_remote https://github.com/<your-username>/ds_s3_uploader

