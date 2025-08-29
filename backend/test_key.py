import os
from dotenv import load_dotenv
import google.generativeai as genai

print("--- Starting API Key Test ---")

# 1. Load environment variables from .env file
print("Step 1: Loading .env file...")
load_dotenv()

# 2. Retrieve the API key
print("Step 2: Retrieving GOOGLE_API_KEY from environment...")
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("❌ FAILURE: GOOGLE_API_KEY not found in environment.")
    print("   - Make sure your file is named '.env' (with a dot).")
    print("   - Make sure the file is in the 'backend' folder.")
    print("   - Make sure the file contains: GOOGLE_API_KEY='your-key-here'")
    exit() # Stop the script if no key is found

print("   ✓ API Key found in environment.")

# 3. Configure the Google AI SDK
print("Step 3: Configuring the Google AI SDK...")
try:
    genai.configure(api_key=api_key)
    print("   ✓ SDK Configured.")
except Exception as e:
    print(f"❌ FAILURE: An error occurred during SDK configuration: {e}")
    exit()

# 4. Make a test API call
print("Step 4: Making a test call to the Gemini API...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello in one word.")

    print("\n✅ SUCCESS! Your API key is working correctly.")
    print(f"   Response from Gemini: {response.text.strip()}")

except Exception as e:
    print("\n❌ FAILURE: The API call failed.")
    print(f"   Error details: {e}")
    print("   This usually means the API key is invalid or has restrictions.")

print("\n--- Test Finished ---")