import requests
import sys
import os
from dotenv import load_dotenv


load_dotenv()
url = "https://www.tadpoles.com/auth/login"


def get_session():
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if email is None:
        sys.exit("Add email env var")
    if password is None:
        sys.exit("Add password env var")

    data: dict[str, str] = {"email": email, "password": password, "service": "tadpoles"}

    session = requests.Session()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://www.tadpoles.com",
        "Connection": "keep-alive",
        "Referer": "https://www.tadpoles.com/home_or_work",
    }

    # session will persist set-cookie return value from response
    response = session.post(url, data, headers=headers)

    if not response.ok:
        sys.exit(f"Error logging in: ({response.status_code})")

    # fetch parents dashboard page to get upgraded set-cookie return value
    # which is needed for subsequent requests
    session.get("https://www.tadpoles.com/parents")

    return session
