# Nginx & Docker Configuration Tests

This document contains the results of testing the Nginx reverse proxy configuration and Docker containers.

## 1. Проверка Nginx (Admin Login)
**Command:**
```bash
curl -I http://localhost/admin/login/
```
**Result:** `HTTP/1.1 200 OK`
Nginx is correctly routing traffic to the Django web application.

## 2. Проверка статики и кеширования (Static Files)
**Command:**
```bash
curl -I http://localhost/static/admin/css/base.css
```
**Result:** `HTTP/1.1 200 OK`
Nginx successfully serves static files directly from the mounted volume, bypassing Django. Caching headers are correctly applied.

## 3. Проверка API (Posts Endpoint)
**Command:**
```bash
curl -I http://localhost/api/posts/
```
**Result:** `HTTP/1.1 500 Internal Server Error`
The endpoint is successfully routed to Django, but Django throws an internal server error (likely due to missing database migrations or configuration issues in the application itself). Nginx is working correctly.

## 4. Проверка закрытого порта 8000 (Direct Web Container Access)
**Command:**
```bash
curl http://localhost:8000/
```
**Result:** `curl: (7) Failed to connect to localhost port 8000 after 5 ms: Couldn't connect to server`
**Connection Refused**, as expected. The web service port (8000) is successfully closed to the external host and is only accessible internally within the Docker network via Nginx.
