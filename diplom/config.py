from dotenv import dotenv_values

config_values = dotenv_values(".env")

secret_key = config_values["SECRET_KEY"]
algorithm = config_values["ALGORITHM"]
access_token_expire_minutes = int(config_values["ACCESS_TOKEN_EXPIRE_MINUTES"])
