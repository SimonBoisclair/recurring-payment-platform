from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RecurPay"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite+aiosqlite:///./data/recurpay.db"

    # PayPal
    paypal_client_id: str = ""
    paypal_client_secret: str = ""
    paypal_base_url: str = "https://api-m.sandbox.paypal.com"  # Use live URL in production

    # Wave
    wave_api_token: str = ""
    wave_business_id: str = ""

    # Admin
    admin_username: str = "admin"
    admin_password: str = "changeme"

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    base_url: str = "http://localhost:8000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
