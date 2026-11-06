import os.path
import csv

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


# Permissions:gmail.readonly: Read your Gmail messages.
#spreadsheets: Read and update Google spreadsheets.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/spreadsheets"
]


# Your Google Spreadsheet ID
SPREADSHEET_ID = "1iES2xM0hM6S0xdRT8W5jVsePcG3ysRQyGUdxdNVo8rc"


def connect_to_google():

    creds = None

    # Check for existing token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            "token.json", SCOPES
        )

    # Authenticate if necessary
    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )

            creds = flow.run_local_server(port=0)

        # Save authentication token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Connect to Gmail
    gmail_service = build(
        "gmail", "v1", credentials=creds
    )

    # Connect to Google Sheets
    sheets_service = build(
        "sheets", "v4", credentials=creds
    )

    print("Successfully connected to Gmail and Google Sheets!")

    return gmail_service, sheets_service


def get_emails(gmail_service):

    # Retrieve latest 10 emails
    results = gmail_service.users().messages().list(
        userId="me",
        maxResults=10
    ).execute()

    messages = results.get("messages", [])

    email_data = []

    # Extract email information
    for message in messages:

        email = gmail_service.users().messages().get(
            userId="me",
            id=message["id"],
            format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = email.get("payload", {}).get("headers", [])

        email_info = {
            "sender": "",
            "subject": "",
            "date": ""
        }

        for header in headers:

            if header["name"].lower() == "from":
                email_info["sender"] = header["value"]

            elif header["name"].lower() == "subject":
                email_info["subject"] = header["value"]

            elif header["name"].lower() == "date":
                email_info["date"] = header["value"]

        email_data.append(email_info)

    return email_data


def save_to_csv(email_data):

    with open(
        "gmail_emails.csv", "w",
        newline="", encoding="utf-8"
    ) as file:

        columns = ["sender", "subject", "date"]

        writer = csv.DictWriter(
            file, fieldnames=columns
        )

        writer.writeheader()
        writer.writerows(email_data)

    print("Emails saved to CSV!")


def save_to_google_sheets(sheets_service, email_data):

    # Prepare spreadsheet data
    values = [
        ["Sender", "Subject", "Date"]
    ]

    for email in email_data:

        values.append([
            email["sender"],
            email["subject"],
            email["date"]
        ])

    # Clear old data to avoid duplicates
    sheets_service.spreadsheets().values().clear(
        spreadsheetId=SPREADSHEET_ID,
        range="Emails!A:Z",
        body={}
    ).execute()

    # Write new data
    sheets_service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range="Emails!A1",
        valueInputOption="RAW",
        body={"values": values}
    ).execute()

    print("Emails successfully saved to Google Sheets!")


if __name__ == "__main__":

    # Connect to Google services
    gmail_service, sheets_service = connect_to_google()

    # Retrieve emails
    email_data = get_emails(gmail_service)

    print(f"Retrieved {len(email_data)} emails.")

    # Save to CSV
    save_to_csv(email_data)

    # Save to Google Sheets
    save_to_google_sheets(sheets_service, email_data)