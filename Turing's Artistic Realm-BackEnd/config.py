from dotenv import load_dotenv
import os

# 加载 .env 文件中的变量
load_dotenv()

VOLCENGINE_ACCESS_KEY = os.getenv('VOLCENGINE_ACCESS_KEY')
VOLCENGINE_SECRET_KEY = os.getenv('VOLCENGINE_SECRET_KEY')
STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
