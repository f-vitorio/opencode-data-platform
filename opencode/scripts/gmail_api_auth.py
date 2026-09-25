#!/usr/bin/env python3
"""
OAuth do Gmail API (escopo gmail.compose) + criação de drafts.

Uso:
  python3 gmail_api_auth.py --auth          # primeira vez: abre consentimento, salva token
  python3 gmail_api_auth.py --create-draft --to ... --subject ... --body-file ...
  python3 gmail_api_auth.py --create-draft --to ... --subject ... --body "..."
  python3 gmail_api_auth.py --list-drafts
"""

import argparse
import base64
import json
import os
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]
CRED_DIR = Path.home() / ".config" / "opencode" / "credentials"
CLIENT_SECRET = CRED_DIR / (
    "client_secret_1096436543776-iuo52suml8tgdtgvfalnbf15rhmq8kfk"
    ".apps.googleusercontent.com.json"
)
TOKEN_PATH = CRED_DIR / "gmail-token.json"


def load_creds() -> Credentials:
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        TOKEN_PATH.write_text(creds.to_json())
        return creds
    return None


def auth_interactive() -> Credentials:
    if not CLIENT_SECRET.exists():
        print(f"ERRO: client secret não encontrado: {CLIENT_SECRET}", file=sys.stderr)
        sys.exit(1)
    flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET), SCOPES)
    # localhost: open browser + local server
    creds = flow.run_local_server(
        port=0,
        access_type="offline",
        prompt="consent",
        open_browser=True,
    )
    TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_PATH.write_text(creds.to_json())
    print(f"Token salvo em: {TOKEN_PATH}")
    return creds


def get_service(creds: Credentials):
    return build("gmail", "v1", credentials=creds)


def create_draft(service, to: str, subject: str, body: str) -> dict:
    from email.message import EmailMessage
    msg = EmailMessage()
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body, charset="utf-8")
    raw = base64.urlsafe_b64encode(bytes(msg)).decode("ascii")
    draft = {"message": {"raw": raw}}
    return service.users().drafts().create(userId="me", body=draft).execute()


def list_drafts(service, limit: int = 10):
    resp = service.users().drafts().list(userId="me", maxResults=limit).execute()
    items = resp.get("drafts", [])
    if not items:
        print("Nenhum rascunho.")
        return
    for d in items:
        meta = service.users().drafts().get(userId="me", id=d["id"], format="metadata").execute()
        headers = (
            meta.get("message", {})
            .get("payload", {})
            .get("headers", [])
        )
        subj = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        try:
            from email.header import decode_header, make_header
            subj = str(make_header(decode_header(subj)))
        except Exception:
            pass
        print(f'- id={d["id"]} subject={subj}')


def main():
    parser = argparse.ArgumentParser(description="Gmail API drafts")
    parser.add_argument("--auth", action="store_true", help="Rodar OAuth interativo")
    parser.add_argument("--create-draft", action="store_true")
    parser.add_argument("--list-drafts", action="store_true")
    parser.add_argument("--to")
    parser.add_argument("--subject")
    parser.add_argument("--body")
    parser.add_argument("--body-file")
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.auth:
        auth_interactive()
        return

    creds = load_creds()
    if not creds:
        print("Sem token válido. Rode: python3 gmail_api_auth.py --auth", file=sys.stderr)
        sys.exit(2)

    service = get_service(creds)

    if args.list_drafts:
        list_drafts(service, args.limit)
        return

    if args.create_draft:
        if not args.to or not args.subject:
            print("--to e --subject são obrigatórios", file=sys.stderr)
            sys.exit(2)
        if args.body_file:
            body = Path(args.body_file).read_text(encoding="utf-8")
        elif args.body is not None:
            body = args.body
        else:
            print("Informe --body ou --body-file", file=sys.stderr)
            sys.exit(2)
        draft = create_draft(service, args.to, args.subject, body)
        print("Draft criado:")
        print(json.dumps({"id": draft.get("id"), "messageId": draft.get("message", {}).get("id")}, indent=2))
        return

    parser.print_help()


if __name__ == "__main__":
    main()
