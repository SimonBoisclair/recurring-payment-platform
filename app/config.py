from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RecurPay"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite+aiosqlite:////data/recurpay.db"

    # PayPal
    paypal_client_id: str = "AdnnJ-Id0-mprwMPrseyPYKw_JAyBLj1TQkShRUFc8GXDDJzXlYpV6bAt852tKO1TG-v1YYtiSCfAbBl"
    paypal_client_secret: str = "EDIoR4_CtkN-PBLTA0JRNZb7ZvtV-gPSGK3IFKuVeyywAgb6VL5zhsLkMqH41c3Uvmn7G8ZvN7SlwCV5"
    paypal_base_url: str = "https://api-m.paypal.com"

    # Wave
    wave_api_token: str = ""
    wave_business_id: str = ""

    # Admin
    admin_username: str = "admin"
    admin_password: str = "changeme"

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    base_url: str = "https://recurring-payment-pla-wurmvkua.fly.dev"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
