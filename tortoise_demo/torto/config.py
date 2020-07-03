# 项目配置文件
from starlette.config import Config
from starlette.datastructures import Secret
from dotenv import find_dotenv

env_path = find_dotenv()
_config = Config(env_path)

TESTING = _config("TESTING", cast=bool, default=False)

AMQ_HOST = _config("AMQ_HOST", default="192.168.1.197")
AMQ_PORT = _config("AMQ_PORT", cast=int, default=61613)
AMQ_USERNAME = _config("AMQ_USERNAME", default="admin")
AMD_PASSWORD = _config("AMD_PASSWORD", cast=Secret, default="admin")


DB_HOST = _config("DB_HOST", default="192.168.1.197")
DB_PORT = _config("DB_PORT", cast=int, default=5432)
DB_USERNAME = _config("DB_USERNAME", default="datacenter1")
DB_PASSWORD = _config("DB_PASSWORD", cast=Secret, default="uxsino")
DB_DRIVER = _config("DB_DRIVER", default="uxdb")
DB_DATABASE = _config("DB_DATABASE", default="dbtest")
SQLALCHEMY_DATABASE_URL = f"{DB_DRIVER}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
# SQLALCHEMY_DATABASE_URL = "sqlite:////home/chauncey/github/simo-web/test.db"

ES_HOST = _config("ES_HOST", default="192.168.1.163")
ES_PORT = _config("ES_PORT", cast=int, default=9200)
ES_URI = [f'http://{ES_HOST}:{ES_PORT}']


EUREKA_SERVER = _config("EUREKA_SERVER", default="http://192.168.2.24:10086/eureka")
DATACENTER_SERVER_HOST = _config("DATACENTER_SERVER_HOST", default="192.168.1.163")
DATACENTER_SERVER_PORT = _config("DATACENTER_SERVER_PORT", cast=int, default=8000)
APP_NAME = _config("APP_NAME", default="datacenter")


TORTOISE_ORM = {
    "connections": {"default": "sqlite:////tmp/test.db"},
    "apps": {
        "models": {
            "models": ["torto.models.__init__", "aerich.models"],
            "default_connection": "default"
        }
    }
}
