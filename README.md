# RecurPay — Recurring Payment Platform

A self-hosted recurring payment platform that lets you manage monthly client subscriptions with PayPal and sync payments to Wave accounting.

## Features

- **Client Management** — Add clients with custom monthly amounts
- **Payment Links** — Each client gets a unique payment link to set up their subscription
- **PayPal Subscriptions** — Automatic recurring credit card billing via PayPal
- **Admin Dashboard** — View all clients, active subscriptions, payment history, and revenue stats
- **Wave Integration** — Sync payments to your Wave accounting for bookkeeping
- **Webhook Support** — Automatic payment recording via PayPal webhooks

## Quick Start

### 1. Install dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Run the server

```bash
cd /path/to/recurring-payment-platform
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. Access the dashboard

Open `http://localhost:8000` and log in with your admin credentials.

## How It Works

### For You (Admin)
1. Log in to the dashboard at `/`
2. Add a client with their name, email, and monthly amount
3. Copy the payment link and send it to your client
4. Monitor subscriptions and payments from the dashboard
5. Optionally sync payments to Wave for bookkeeping

### For Your Clients
1. Open the payment link you sent them
2. Review the subscription details
3. Subscribe via PayPal (supports credit/debit cards)
4. Payments are charged automatically each month

## PayPal Setup

1. Go to [PayPal Developer Dashboard](https://developer.paypal.com/dashboard/applications)
2. Create a new app (use Sandbox for testing, Live for production)
3. Copy the **Client ID** and **Secret** to your `.env`
4. Set the webhook URL in PayPal to: `https://your-domain.com/webhooks/paypal`
5. Subscribe to these webhook events:
   - `PAYMENT.SALE.COMPLETED`
   - `BILLING.SUBSCRIPTION.CANCELLED`

## Wave Setup

1. Go to [Wave Developer](https://developer.waveapps.com/)
2. Create an application and get your API token
3. Find your business ID from the Wave API
4. Add both to your `.env`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/login` | Admin login |
| GET | `/api/dashboard` | Dashboard stats |
| GET | `/api/clients` | List all clients |
| POST | `/api/clients` | Create a client |
| PUT | `/api/clients/{id}` | Update a client |
| DELETE | `/api/clients/{id}` | Delete a client |
| GET | `/api/payments` | List payments |
| POST | `/webhooks/paypal` | PayPal webhook receiver |
| GET | `/pay/{token}` | Client payment page |

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy (async SQLite)
- **Frontend**: Vanilla HTML/CSS/JS
- **Payments**: PayPal Subscriptions API
- **Accounting**: Wave GraphQL API
