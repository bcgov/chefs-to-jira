"""
ESS Pull Consumer with Cryptr Decryption + Email

Features:
- Connects to NATS JetStream (ESS)
- Pull-based consumer (durable)
- Polls every 5 minutes
- Extracts payload.data from CHEFS message
- Decrypts using Cryptr (Node.js bridge)
- Sends ONE email per batch (readable JSON)
- Acknowledges ONLY on success
- Skips failed decrypts
- Clean shutdown (no session leaks)

Requirements:
- Node.js installed
- npm install cryptr
- decrypt_cryptr.js in same directory
"""

import asyncio
import subprocess
import json
import smtplib
import shutil

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from nats.aio.client import Client as NATS
import constants

from datetime import datetime, timedelta, timezone
from nats.js.api import ConsumerConfig, DeliverPolicy


POLL_INTERVAL_SECONDS = 300  # 5 minutes

SCRIPT_DIR = Path(__file__).resolve().parent
CRYPTR_SCRIPT = SCRIPT_DIR / "decrypt_cryptr.js"

# ------------------------------------------------------------
# Seed file (NKey authentication)
# ------------------------------------------------------------

def ensure_seed_file():
    """
    Ensures NATS seed file exists on disk.
    """
    seed_path = Path("./ess-nkey.seed")

    if not seed_path.exists():
        print("[INFO] Writing seed file...")
        seed_path.write_text(constants.ESS_NKEY_SEED)

    return str(seed_path)


# ------------------------------------------------------------
# Cryptr Decryption (Node bridge)
# ------------------------------------------------------------

def decrypt_with_cryptr(encrypted_payload: str, key: str) -> str:
    """
    Calls Node.js Cryptr to decrypt a payload.

    Returns decrypted string OR error string.
    """

    node_path = shutil.which("node")

    if not node_path:
        return "[DECRYPTION FAILED] Node.js not found in PATH"

    try:
        result = subprocess.run(
            [
                node_path,
                str(CRYPTR_SCRIPT),
                key,
                encrypted_payload
            ],
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout.strip()

    except subprocess.CalledProcessError as e:
        return f"[DECRYPTION FAILED]\n{e.stderr.strip()}"


# ------------------------------------------------------------
# Email helper
# ------------------------------------------------------------

def send_email(message_body: str) -> bool:
    """
    Sends email using configured SMTP server.
    """

    try:
        msg = MIMEMultipart()
        msg["From"] = constants.FROM_EMAIL
        msg["To"] = constants.DEBUG_EMAIL
        msg["Subject"] = "Pull Consumer Received Submission"

        msg.attach(MIMEText(message_body, "plain"))

        with smtplib.SMTP(constants.SMTP_SERVER) as server:
            server.send_message(msg)

        print("[INFO] Email sent successfully.")
        return True

    except Exception as e:
        print("[ERROR] Email failed:", str(e))
        return False


# ------------------------------------------------------------
# Fetch messages (NO ack yet)
# ------------------------------------------------------------

async def fetch_messages(sub):
    """
    Pulls messages with a controlled batch size.
    """

    try:
        msgs = await sub.fetch(
            constants.ESS_MAX_MESSAGES,
            timeout=5
        )
        return msgs

    except Exception:
        return []


# ------------------------------------------------------------
# Main consumer
# ------------------------------------------------------------

async def run():
    print("[INFO] Starting ESS pull consumer (Cryptr mode)...")

    seed_file = ensure_seed_file()
    key = constants.ESS_ENCRYPTION_KEY

    nc = NATS()

    await nc.connect(
        servers=[constants.ESS_SERVER],
        user=constants.ESS_NKEY_USER,
        nkeys_seed=seed_file
    )

    js = nc.jetstream()

    print("[INFO] Creating/attaching pull subscription...")

    # ------------------------------------------------------------
    # Set start time = NOW minus 1 hour
    # JetStream expects UTC
    # ------------------------------------------------------------

    start_time = datetime.now(timezone.utc) - timedelta(hours=1)

    # ✅ Convert to ISO string (JetStream expects this)
    start_time_iso = start_time.isoformat()

    print(f"[INFO] Consumer start time (UTC): {start_time_iso}")

    # ------------------------------------------------------------
    # Configure consumer to ONLY read recent messages
    # ------------------------------------------------------------

    consumer_config = ConsumerConfig(
        durable_name=constants.ESS_DURABLE_NAME,
        deliver_policy=DeliverPolicy.BY_START_TIME,
        opt_start_time=start_time_iso,
        # Optional but clean practice
        ack_policy="explicit",
    )

    sub = await js.pull_subscribe(
        subject=constants.ESS_FILTER_SUBJECTS,
        durable=constants.ESS_DURABLE_NAME,
        stream=constants.ESS_STREAM_NAME,
        config=consumer_config
    )

    try:
        while True:
            print("[INFO] Polling for messages...")

            msgs = await fetch_messages(sub)

            if not msgs:
                print("[INFO] No messages found.")
                await asyncio.sleep(POLL_INTERVAL_SECONDS)
                continue

            decrypted_payloads = []
            ack_candidates = []

            for msg in msgs:
                try:
                    raw_json = msg.data.decode()
                    parsed = json.loads(raw_json)

                    print("\n[RAW MESSAGE]")
                    print(raw_json)

                    # ✅ Extract encrypted payload correctly
                    encrypted_payload = parsed["payload"]["data"]

                    decrypted = decrypt_with_cryptr(encrypted_payload, key)

                    if decrypted.startswith("[DECRYPTION FAILED]"):
                        print("[WARN] Decryption failed — skipping")
                        print(decrypted)
                        continue

                    print("[DECRYPTED]")
                    print(decrypted)

                    # Pretty print JSON if possible
                    try:
                        parsed_json = json.loads(decrypted)
                        decrypted = json.dumps(parsed_json, indent=2)
                    except Exception:
                        pass

                    decrypted_payloads.append(decrypted)
                    ack_candidates.append(msg)

                except Exception as e:
                    print("[ERROR] Processing message:", str(e))

            # ✅ Only send email if we have valid decrypted payloads
            if decrypted_payloads:
                email_body = "\n\n--- MESSAGE ---\n\n".join(decrypted_payloads)

                if send_email(email_body):
                    print("[INFO] Acknowledging messages...")

                    for msg in ack_candidates:
                        await msg.ack()
                else:
                    print("[WARN] Email failed — messages NOT acked (retry later)")

            else:
                print("[INFO] No valid decrypted messages to send.")

            await asyncio.sleep(POLL_INTERVAL_SECONDS)

    finally:
        print("[INFO] Closing NATS connection...")
        await nc.close()


# ------------------------------------------------------------
# Entry
# ------------------------------------------------------------

if __name__ == "__main__":
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        print("\n[INFO] Stopped cleanly.")
