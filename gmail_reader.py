import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Permission required: read Gmail messages
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def connect_to_gmail():

    creds = None

    # Check whether we already have an access token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json", SCOPES
        )

    # If no valid token exists, ask Google for permission
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save the token for future use
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Build Gmail API service
    service = build("gmail", "v1", credentials=creds)

    print("Successfully connected to Gmail!")

    return service


if __name__ == "__main__":

    # Connect to Gmail
    gmail_service = connect_to_gmail()

    # Get the latest 10 email messages
    results = gmail_service.users().messages().list(
        userId="me",
        maxResults=10
    ).execute()

    messages = results.get("messages", [])

    print(f"\nTotal emails retrieved: {len(messages)}")

    # Read each email
    for message in messages:

        email = gmail_service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = email["payload"]["headers"]

        print("\n----------------------------")

        for header in headers:
            if header["name"] in ["From", "Subject", "Date"]:
                print(header["name"] + ":", header["value"])