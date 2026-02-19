# NoirVault – High-Performance Premium Fashion E-Commerce Platform

================================================================================
TABLE OF CONTENTS
================================================================================
1. Project Overview & Core Mission
2. Technical Architecture & Tech Stack
3. Core Features & Business Logic
4. Advanced Payment Lifecycle Design (Webhook-First)
5. Security Hardening & Best Practices
6. Distributed System & Concurrency Engineering
7. Database Schema & Data Integrity
8. Failure Recovery & edge Case Handling
9. Deployment Specifications (Railway/Production)
10. Future Roadmap & Scalability
11. Resume Technical Summary

================================================================================
1. PROJECT OVERVIEW & CORE MISSION
================================================================================
**NoirVault** is a production-hardened, full-stack e-commerce platform built with Django. 
Designed for high reliability and financial correctness, it serves as a robust 
foundation for premium fashion retail (Dark Luxury Aesthetic).

**Core Mission:**
To move beyond "tutorial-level" implementations and demonstrate mastery of:
- Use of atomic transactions for financial integrity.
- Pessimistic locking for inventory management.
- Webhook-driven event processing vs. fragile client-side logic.
- Idempotency in distributed systems.

**Why It Was Built:**
To solve the "Paid but No Order" problem inherent in simple checkout flows where 
network latency or user behavior (closing tabs) leads to data inconsistency.

================================================================================
2. TECHNICAL ARCHITECTURE & TECH STACK
================================================================================
**Architecture Type:** 
Monolithic MVC (Model-View-Controller) optimized for strict data consistency.

**Backend:**
- **Framework:** Django 5.0 (Python 3.12)
- **WSGI Server:** Gunicorn (Production)
- **Asynchronous Tasks:** Threaded Webhook Processing (Sync fallback)

**Database:**
- **Primary:** PostgreSQL (Production via Railway Plugin)
- **Development:** SQLite3 (Local)
- **ORM:** Django ORM with `dj-database-url`

**Frontend:**
- **Template Engine:** Django Templates (Server-Side Rendered)
- **Styling:** Tailwind CSS (Utility-First)
- **Design System:** "Dark Luxury" (Minimalist, High Contrast)

**Infrastructure:**
- **Hosting:** Railway (PaaS)
- **Static Files:** WhiteNoise (Compressed/Cached Serving)
- **Payments:** Stripe API (Checkout & Webhooks)
- **Environment:** strict .env variable isolation via python-dotenv

================================================================================
3. CORE FEATURES & BUSINESS LOGIC
================================================================================
**Authentication & User Management:**
- Custom User Model (AbstractUser not needed yet, standard User used)
- Role-Based Access Control (RBAC): Admin vs. Standard Customer
- Secure Login/Logout/Signup flows with validation

**Catalog & Inventory:**
- Product Management (CRUD via Admin)
- Category Hierarchies using persistent Slugs
- Image Handling with CDN-ready URL fields
- Automated Stock Tracking (Decrement on Order, Restore on Cancel)

**Shopping Cart:**
- Session-Based Persistence (No database overhead for guest carts)
- AJAX-free robust add/update/remove actions
- Logic to prevent adding > available stock

**Order Management:**
- Immutable Order Records
- Order Item Snapshots (Price at time of purchase preserved)
- Cancellation Workflow with Atomic Stock Restoration

**Analytics Dashboard:**
- Admin-only view of Revenue, Sales Count, and Low Stock Alerts.
- Aggregate queries using Django `Sum` and `Count`.

================================================================================
4. ADVANCED PAYMENT LIFECYCLE DESIGN (WEBHOOK-FIRST)
================================================================================
The most critical engineering component of NoirVault is the decoupling of 
payment success from the user interface.

**The "Old" (Fragile) Way:**
1. User Pays on Stripe.
2. Stripe Redirects User to `/success/`.
3. `/success/` view creates the Order.
*Failure Point:* If user closes tab or loses internet *after* step 1 but *before* step 3, 
money is taken but no order exists.

**The NoirVault (Robust) Way:**
1. **Metadata Injection:** Cart state and User ID are serialized into the Stripe Session Metadata during Checkout creation.
2. **Authorize & Capture:** User pays on Stripe.
3. **Async Event:** Stripe sends a `checkout.session.completed` webhook to NoirVault.
4. **Server-Side Fulfillment:** 
   - NoirVault validates the signature.
   - Decodes metadata.
   - Locks the database rows.
   - Creates the order.
5. **Client Polling:** The User is redirected to `/success/`, which simply displays the Order provided by the background worker.

**Result:** 
100% Reliability. Even if the user throws their laptop out the window after clicking "Pay", the order is fulfilled.

================================================================================
5. SECURITY HARDENING & BEST PRACTICES
================================================================================
**Cryptographic Verification:**
All webhooks must pass `stripe.Webhook.construct_event()` validation using the `STRIPE_WEBHOOK_SECRET`. 
This makes it mathematically impossible to spoof a payment event.

**Environment Isolation:**
The application refuses to boot if critical secrets (`SECRET_KEY`, `STRIPE_API_KEY`) are missing. 
`DEBUG` is strictly enforced via environment variables (`False` in production).

**Idempotency & Replay Protection:**
The `Order` model enforces `unique=True` on `stripe_payment_id`. 
If Stripe sends the same webhook event 5 times (due to network retries), 
NoirVault processes it once and returns 200 OK for the rest, preventing duplicate orders.

**Standard Defenses:**
- **CSRF Protection:** Enabled globally.
- **SQL Injection:** Mitigated via Django ORM parameterization.
- **XSS:** Default Django template auto-escaping enabled.
- **Clickjacking:** `X-Frame-Options: DENY`.
- **SSL:** `SECURE_SSL_REDIRECT` enabled in production.

================================================================================
6. DISTRIBUTED SYSTEM & CONCURRENCY ENGINEERING
================================================================================
An e-commerce system must handle **Race Conditions**.
*Scenario:* Item A has 1 unit of stock. User 1 and User 2 checkout simultaneously.

**NoirVault's Solution: Pessimistic Locking**
Start Transaction (`atomic`)
   Query Product with `select_for_update()` -> LOCKS ROW
   Check Stock > 0?
       Yes: Decrement Stock, Create Order, Commit.
       No: Raise ValueError, Rollback.
End Transaction

**Auto-Refund Mechanism:**
If the Lock is acquired but stock is gone (The "Oversell" Edge Case), 
NoirVault catches the `ValueError` and immediately calls `stripe.Refund.create()`.
This ensures integrity: The user is not charged for an item they didn't win.

================================================================================
7. DATABASE SCHEMA & DATA INTEGRITY
================================================================================
**Models:**
- `User` (FK) -> `Order`
- `Order` -> `OrderItem` (One-to-Many)
- `Product` -> `Category` (FK)

**Constraints:**
- `stripe_payment_id`: UNIQUE (Idempotency Key)
- `slug`: UNIQUE (Category URL safety)
- `stock`: Non-Negative (Enforced via Logic)

**Transactions:**
All financial mutations (Checkout, Refund, Cancellation) act within 
`transaction.atomic()` blocks to verify ACID compliance.

================================================================================
8. FAILURE RECOVERY & EDGE CASE HANDLING
================================================================================
| Failure Scenario | System Response |
| :--- | :--- |
| **User Closes Tab** | Webhook handles fulfillment independently. |
| **Concurrent Oversell** | DB Lock -> Stock Check Fail -> Auto-Refund API Call. |
| **Webhook Retry** | Idempotency Check -> Return 200 OK (Ignore). |
| **Metadata Corruption** | JSON Decode Error -> Log Failure -> Return 400. |
| **Deleted User/Product** | `DoesNotExist` Exception -> Auto-Refund -> Log. |
| **Direct URL Attack** | `/success/` verifies session ID with Stripe. |

================================================================================
9. DEPLOYMENT SPECIFICATIONS
================================================================================
**Platform:** Railway (Recommended) or Heroku
**Runtime:** Python 3.12+
**Entrypoint:** `gunicorn noirvault.wsgi`

**Required Environment Variables:**
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=.railway.app`
- `DATABASE_URL=postgres://...`
- `STRIPE_PUBLIC_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_WEBHOOK_SECRET`
- `BACKEND_DOMAIN` (e.g., https://noirvault.up.railway.app)

**Post-Deploy Steps:**
1. `python manage.py migrate`
2. `python manage.py collectstatic`
3. Configure Stripe Webhook URL to: `/webhook/stripe/`

================================================================================
10. FUTURE ROADMAP & SCALABILITY (v2)
================================================================================
- **Redis Caching:** Cache product list views to reduce DB read load.
- **Celery Workers:** Move email sending out of the webhook request/response cycle.
- **Wishlist Functionality:** Allow users to save items for later.
- **Guest Checkout:** Reduce friction by allowing purchase without account.
- **Recommendation Engine:** "You might also like" based on vector embeddings.

================================================================================
11. RESUME TECHNICAL SUMMARY
================================================================================
**Full-Stack Django Engineer | NoirVault**
Architected and deployed a secure, production-grade e-commerce platform handling 
real-time payments and inventory. I engineered a robust **webhook-first payment lifecycle** 
to eliminate "paid-no-order" discrepancies, utilizing **atomic transactions** and 
**pessimistic locking (PostgreSQL)** to resolve high-concurrency race conditions. 
Implements automated refund logic for edge-case failures and limits exposure via 
strict **idempotency** handling for distributed event retries. Hardened security via 
cryptographic signature verification and environment isolation, delivering a 
fail-safe financial system.
