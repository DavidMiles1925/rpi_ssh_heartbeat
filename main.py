#!/usr/bin/env python3
"""
Check SSH connectivity to a list of Raspberry Pis using the system ssh client.

Enhancements:
- Retries once on failure
- Sends ntfy notification if any failures occur
"""

import os
import sys
import logging
import shutil
import subprocess
import time
import urllib.request

from config import rpis, ntfy_topic

# --- Configuration ---
RPIS = rpis

KEY_PATH = r"C:\Users\David\.ssh\id_rsa"
SSH_PORT = 22
CONNECT_TIMEOUT = 6
RETRY_DELAY = 2  # seconds between retry attempts

LOG_FILE = os.path.expanduser("~/rpi_ssh_check.log")
SSH_BINARY = shutil.which("ssh")

NTFY_TOPIC = ntfy_topic
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
# ----------------------

if SSH_BINARY is None:
    print("ERROR: ssh binary not found in PATH. Install OpenSSH client.", file=sys.stderr)
    sys.exit(1)


def setup_logger(log_file):
    logger = logging.getLogger("rpi_ssh_check")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s %(levelname)-7s %(message)s")

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    fh = logging.FileHandler(log_file)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger


def check_with_ssh(ip, username, key_path=None, port=22, timeout=10):
    cmd = [
        SSH_BINARY,
        "-o", "BatchMode=yes",
        "-o", f"ConnectTimeout={int(timeout)}",
        "-o", "PasswordAuthentication=no",
        "-o", "PreferredAuthentications=publickey",
        "-p", str(port),
    ]

    if key_path:
        cmd += ["-i", key_path]

    cmd += [f"{username}@{ip}", "exit"]

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout 
        )
        if proc.returncode == 0:
            return True, "Connected"
        else:
            errmsg = proc.stderr.strip() or f"ssh exited {proc.returncode}"
            return False, errmsg

    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout}s"
    
    except Exception as e:
        return False, f"Failed to run ssh: {e}"


def send_ntfy_notification(message):
    try:
        data = message.encode("utf-8")
        req = urllib.request.Request(NTFY_URL, data=data, method="POST")
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        # Don't crash script if notification fails
        print(f"Failed to send ntfy notification: {e}", file=sys.stderr)


def main():
    logger = setup_logger(LOG_FILE)
    logger.info("Starting Raspberry Pi SSH connectivity check")

    failures = []

    for name, cfg in RPIS.items():
        ip = cfg["ip"]
        username = cfg["user"]

        logger.info(f"Checking {name} ({ip}) ...")

        # --- First attempt ---
        ok, msg = check_with_ssh(ip, username, key_path=KEY_PATH, port=SSH_PORT, timeout=CONNECT_TIMEOUT)

        # --- Retry once if failed ---
        if not ok:
            logger.warning(f"{name} ({ip}) failed, retrying in {RETRY_DELAY}s...")
            time.sleep(RETRY_DELAY)
            ok, msg = check_with_ssh(ip, username, key_path=KEY_PATH, port=SSH_PORT, timeout=CONNECT_TIMEOUT)

        if ok:
            logger.info(f"{name} ({ip}) - OK: {msg}")
        else:
            logger.error(f"{name} ({ip}) - FAILED: {msg}")
            failures.append((name, ip, msg))

    # --- Final result ---
    if failures:
        logger.warning(f"Completed with {len(failures)} failure(s).")

        failure_lines = []
        for name, ip, msg in failures:
            line = f"{name} ({ip}): {msg}"
            logger.warning(f" - {line}")
            failure_lines.append(line)

        # Send ntfy alert
        notification_message = "RPI SSH Check FAILED:\n" + "\n".join(failure_lines)
        send_ntfy_notification(notification_message)

        sys.exit(2)
    else:
        logger.info("All Raspberry Pis reachable via SSH.")
        sys.exit(0)


if __name__ == "__main__":
    main()