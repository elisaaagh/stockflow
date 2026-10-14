from database.db import get_connection


def main():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        current_database(),
                        current_user
                """)

                result = cursor.fetchone()

                print("Connection successful!")
                print(f"Database: {result[0]}")
                print(f"User: {result[1]}")

    except Exception as error:
        print(f"Connection failed: {error}")


if __name__ == "__main__":
    main()
