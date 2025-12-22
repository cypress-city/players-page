import os
from dotenv import load_dotenv
from modules.bot import Bot


if __name__ == "__main__":
    load_dotenv()
    Bot().run(os.getenv("TOKEN"))
