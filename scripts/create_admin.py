
from getpass import getpass

from api.security import hash_password
from database.users import (
    create_user,
    get_user_by_username
)


def main():
    print("=== StockFlow Admin Setup ===")

    username = input("Admin username: ").strip().lower()

    if len(username) < 3 or len(username) > 50:
        print("Username must contain 3 to 50 characters.")
        return

    if get_user_by_username(username):
        print("This username already exists.")
        return

    password = getpass("Password: ")
    confirmation = getpass("Confirm password: ")

    if password != confirmation:
        print("Passwords do not match.")
        return

    try:
        password_hash = hash_password(password)
    except ValueError as error:
        print(error)
        return

    user_id = create_user(
        username=username,
        password_hash=password_hash,
        role="admin"
    )

    print(f"Administrator created. User ID: {user_id}")


if __name__ == "__main__":
    main()
