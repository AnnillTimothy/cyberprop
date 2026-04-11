# CyberProp — Smart Property Management Platform

A Django-based property management SaaS application with integrated e-commerce, investor dashboards, and PayFast payment processing. Built with a cyberpunk-themed dark UI.

## Features

- **Property Listings** — Browse, search, and filter rental properties by city, type, price, and bedrooms
- **Tenant & Owner Portals** — Role-based accounts for tenants, property owners, staff, and admins
- **Admin Dashboard** — Full management interface with KPI cards, charts, and reports
- **Property Management** — Income/expense tracking, maintenance requests, cleaning schedules, and investor payouts
- **E-Commerce Store** — Merchandise store with cart, checkout, and PayFast payment integration
- **Booking System** — Schedule property viewings with status tracking
- **Enquiry System** — Property enquiries for non-logged-in users

## Tech Stack

- **Backend:** Django 6.0 (Python)
- **Database:** SQLite (development) — easily swappable for PostgreSQL
- **Frontend:** Bootstrap 5.3 (dark theme), GSAP ScrollTrigger animations
- **Payments:** PayFast (South African gateway)
- **Static Files:** WhiteNoise for production serving
- **Forms:** django-crispy-forms with Bootstrap 5 pack

## Project Structure

```
cyberprop/
├── cyberprop_project/    # Django project settings & root URL config
├── core/                 # Homepage, about, contact, legal pages
├── accounts/             # Custom user model, auth (login/register/profile)
├── properties/           # Property listings, bookings, enquiries, submissions
├── dashboard/            # Staff/admin management dashboard
├── management_app/       # Property financials, maintenance, payouts, cleaning
├── store/                # E-commerce store with PayFast integration
├── templates/            # Global base template
└── static/               # CSS and JavaScript assets
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AnnillTimothy/cyberprop.git
   cd cyberprop
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/macOS
   venv\Scripts\activate      # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files (production):**
   ```bash
   python manage.py collectstatic
   ```

8. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

   Visit `http://127.0.0.1:8000/` to see the application.

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Django secret key | Insecure fallback (change in production) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `EMAIL_HOST_USER` | SMTP email user | — |
| `EMAIL_HOST_PASSWORD` | SMTP email password | — |
| `PAYFAST_MERCHANT_ID` | PayFast merchant ID | — |
| `PAYFAST_MERCHANT_KEY` | PayFast merchant key | — |
| `PAYFAST_PASSPHRASE` | PayFast passphrase | — |
| `PAYFAST_SANDBOX` | Use PayFast sandbox | `True` |

## User Roles

| Role | Access |
|---|---|
| **Tenant** | Browse properties, book viewings, shop in store |
| **Property Owner** | Submit properties for management, view submissions |
| **Staff** | Dashboard, property management, maintenance, financials |
| **Admin** | Full access including user management and reports |

## License

This project is proprietary. All rights reserved.