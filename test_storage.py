import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load credentials from your .env file
load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")

if not url or not key:
    print("Error: Missing Supabase credentials in .env")
    exit(1)

supabase: Client = create_client(url, key)

# --- CONFIGURATION ---
# Replace these with the email/password of the test user you created in Supabase Auth
TEST_EMAIL = "test@tuklascope.com"
TEST_PASSWORD = "123"


def test_storage():
    try:
        # 1. Authenticate as the user (Simulating Flutter login)
        print("Logging in...")
        auth_response = supabase.auth.sign_in_with_password(
            {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        )
        user_id = auth_response.user.id
        print(f"Success! Authenticated as User ID: {user_id}")

        # 2. Define the exact path dictated by our RLS policy: scans/{user_id}/dummy.jpg
        file_path = f"{user_id}/dummy.jpg"

        # 3. Attempt the Upload
        print(f"Attempting to upload to: scans/{file_path}")
        with open("dummy.jpg", "rb") as f:
            # We use file_options to set the content-type so it renders as an image in browsers
            supabase.storage.from_("scans").upload(
                file=f,
                path=file_path,
                file_options={"content-type": "image/jpeg"}
            )

        print("Upload successful! RLS allowed the insert.")

        # 4. Generate the Public URL (Simulating what Flutter sends to the /save endpoint)
        public_url = supabase.storage.from_("scans").get_public_url(file_path)
        print(f"\nPublic URL generated:\n{public_url}")
        print("\nTest passed. You can now use this URL in your curl /save payload.")

    except Exception as e:
        print(f"\nTest Failed: {str(e)}")
        print("If it says 'new row violates row-level security policy', your folder path or auth state is wrong.")


if __name__ == "__main__":
    test_storage()
