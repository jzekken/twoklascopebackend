import os
import sys
from dotenv import load_dotenv
from supabase import create_client

print("1. Script started successfully...")

# Force load the .env file
load_dotenv()
print("2. .env file loaded...")

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_ANON_KEY")

if not url or not key:
    print("❌ ERROR: Could not find SUPABASE_URL or SUPABASE_ANON_KEY in your .env file!")
    sys.exit(1)

print("3. Keys found! Connecting to Supabase...")

try:
    supabase = create_client(url, key)

    # Using the dummy user we made earlier
    email = "test@tuklascope.com"
    password = "123"

    print(f"4. Attempting login for {email}...")

    response = supabase.auth.sign_in_with_password(
        {"email": email, "password": password})

    print("\n=== SUCCESS! YOUR NEW JWT TOKEN (Copy the giant string below) ===\n")
    print(response.session.access_token)
    print("\n=================================================================\n")

except Exception as e:
    print(f"\n❌ Login failed: {str(e)}")
