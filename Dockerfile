FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
COPY app/ app/
COPY static/ static/
COPY templates/ templates/

RUN pip install --no-cache-dir . && pip install --no-cache-dir "fastapi[standard]"

ENV PAYPAL_CLIENT_ID=Aapx3IXDTdslAech2JY9tZ1AU1QwdqjSiXjQ2Y2ES3rEPYGEMsmhnUuPN_82mgNMEN55w5sEHmw5LuJq
ENV PAYPAL_CLIENT_SECRET=EOMZB0HkcvwsvPoVrE4jof7qPH4VMkCLTLvAlEEa6fV_vivgIpWWau6FtBOeB-jGbm-d63LmaP-hvn4K
ENV PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
ENV DATABASE_URL=sqlite+aiosqlite:////data/recurpay.db
ENV BASE_URL=https://recurring-payment-pla-wurmvkua.fly.dev

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]
