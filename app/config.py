from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RecurPay"
    secret_key: str = "change-me-in-production"
    database_url: str = "sqlite+aiosqlite:////data/recurpay.db"

    # PayPal
    paypal_client_id: str = "AaCTbm8kpOu4XdhQ39jc4u-g12NML4VAZuh9bVxESr6wX5PUlupVHxODoMEvKA2EG4TLlvJJ6DPikqHb"
    paypal_client_secret: str = "EJo5rlovBPZG4tP4xrpiXM3-16XmZr9v9Tsz9ZBpArXpxxQ1V-a7ma3yE7tMGyw_VeQCEKCHueGiuoe9"
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
