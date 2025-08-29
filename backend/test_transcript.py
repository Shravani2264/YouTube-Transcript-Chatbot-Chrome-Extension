from youtube_transcript_api import YouTubeTranscriptApi

# A well-known video ID that definitely has English captions
TEST_VIDEO_ID = 'RoR4XJw8wIc'  

print(f"--- Starting Transcript Test for video ID: {TEST_VIDEO_ID} ---")

try:
    # 1. Attempt to fetch the transcript
    print("Step 1: Fetching transcript from YouTube...")
    transcript_list = YouTubeTranscriptApi().fetch(TEST_VIDEO_ID, languages=["en"])

    # 2. Process and display a snippet if successful
    transcript_text = " ".join(chunk.text for chunk in transcript_list)

    print("\n✅ SUCCESS! Transcript was fetched correctly.")
    print("\nTranscript snippet:")
    print("-" * 20)
    print(transcript_text[:300] + "...") # Print the first 300 characters
    print("-" * 20)

except Exception as e:
    # 3. If it fails, print the exact error
    print("\n❌ FAILURE: Could not fetch the transcript.")
    print("   This means there might be a network issue or a problem with the API library itself.")
    print("\n--- ERROR DETAILS ---")
    import traceback
    traceback.print_exc() # Print the full detailed error

print("\n--- Test Finished ---")