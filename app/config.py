from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RecurPay"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite+aiosqlite:////data/recurpay.db"

    # PayPal
    paypal_client_id: str = "Aapx3IXDTdslAech2JY9tZ1AU1QwdqjSiXjQ2Y2ES3rEPYGEMsmhnUuPN_82mgNMEN55w5sEHmw5LuJq"
    paypal_client_secret: str = "EOMZB0HkcvwsvPoVrE4jof7qPH4VMkCLTLvAlEEa6fV_vivgIpWWau6FtBOeB-jGbm-d63LmaP-hvn4K"
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

    base_url: str = "https://recurring-payment-pla-wurmvkua.fly.dev"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
