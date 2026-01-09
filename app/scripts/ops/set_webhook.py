#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Set/Delete Telegram webhook reading config from app/core/config.py

Usage examples:

  # Set webhook (reads TELEGRAM_BOT_TOKEN and WEBHOOK_SECRET from Settings)
  python -m app.tools.set_webhook --url https://<your-ngrok>.ngrok-free.app
  https://951ebe3b1ef6.ngrok-free.app 
  python -m app.tools.set_webhook --url https://951ebe3b1ef6.ngrok-free.app

  # Get webhook info
  python -m app.tools.set_webhook --info

  # Delete webhook
  python -m app.tools.set_webhook --delete
"""

from __future__ import annotations
import argparse
import sys
import json
import requests

from app.core.config import settings


def _tg(method: str, payload: dict | None = None):
    base = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/{method}"
    try:
        if payload is None:
            r = requests.get(base, timeout=15)
        else:
            r = requests.post(base, data=payload, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[ERROR] Telegram API call failed: {e}")
        if 'r' in locals():
            try:
                print("[DETAIL]", r.text)
            except Exception:
                pass
        sys.exit(2)


def set_webhook(public_base_url: str):
    url = public_base_url.rstrip('/') + '/webhook/telegram'
    if settings.WEBHOOK_SECRET:
        url += f"?token={settings.WEBHOOK_SECRET}"
    payload = {
        'url': url,
        'drop_pending_updates': 'true',
        'allowed_updates': '["message","callback_query"]',
    }
    res = _tg('setWebhook', payload)
    print(json.dumps(res, ensure_ascii=False, indent=2))


def delete_webhook():
    res = _tg('deleteWebhook', {})
    print(json.dumps(res, ensure_ascii=False, indent=2))


def get_info():
    res = _tg('getWebhookInfo', None)
    print(json.dumps(res, ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser(description='Manage Telegram webhook (reads config.py Settings)')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--info', action='store_true', help='Show current webhook info')
    g.add_argument('--delete', action='store_true', help='Delete current webhook')
    ap.add_argument('--url', help='Public base URL (e.g., https://<ngrok>.ngrok-free.app) for setWebhook')
    args = ap.parse_args()

    if args.info:
        return get_info()
    if args.delete:
        return delete_webhook()
    if not args.url:
        ap.error('--url is required to setWebhook (or use --info/--delete)')
    return set_webhook(args.url)


if __name__ == '__main__':
    main()

