from os import getenv
import platform

plat = str(platform.platform()).lower()

env_path = '/var/www/app/.env' if "linux" in plat else ".env"