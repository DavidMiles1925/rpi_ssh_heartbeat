# Raspberry Pi SSH Connectivity Checker

A lightweight Python script that checks SSH connectivity to a list of Raspberry Pi devices and alerts you if any are unreachable.

Designed to be simple, reliable, and automation-friendly.

This tool acts as a simple monitoring layer for your Raspberry Pis:

- Fast to run
- Easy to automate
- Immediately alerts you when something breaks

Perfect for home labs, IoT setups, or small-scale infrastructure.

---

## 🚀 Features

- ✅ Checks SSH connectivity using the system SSH client
- 🔁 Retries once on failure
- ⏱️ Hard timeout to prevent hangs
- 📝 Logs results to console and file
- 🔔 Sends push notifications via `ntfy` on failure
- 🔒 Keeps sensitive configuration out of source control

---

## 🔐 Configuration (Important)

Device details are stored in a separate `config.py` file to keep them private. Create this file upon first use. Set it up using the example below:

### Example `config.py`

```python
rpis = {
    "rpi_1": {"ip": "192.168.0.111", "user": "squirtle"},
    "rpi_2": {"ip": "192.168.0.120", "user": "pikachu"},
}
```

### `.gitignore`

Make sure this file is ignored:

```
config.py
```

---

## ⚙️ Setup

### 1. Install Requirements

- Python 3.x
- OpenSSH client available in your system PATH

Test SSH is available:

```
ssh -V
```

---

### 2. Configure SSH Access

Ensure:

- Your SSH key is set up (`~/.ssh/id_rsa` or custom path)
- Your public key is added to each Raspberry Pi (`~/.ssh/authorized_keys`)

Instructions Here: [Set Up SSH Key](https://github.com/DavidMiles1925/pi_zero_setup#set-up-ssh-key-to-eliminate-need-for-password)

---

### 3. Update Script Configuration

In `main.py`, adjust:

```python
KEY_PATH = r"C:\Users\YourUser\.ssh\id_rsa"
```

Or set to `None` to use your SSH agent/default keys.

---

### 4. Run the Script

```
python main.py
```

---

### Scheduling (Recommended)

Use **Windows Task Scheduler** to run the script daily.

Recommended settings:

- Run whether user is logged in or not
- Wake the computer to run
- Add trigger "At startup" as backup

---

## Program Details

### Notifications (ntfy)

The script sends a notification if any device fails.

#### To change:

Within `config.py`:

```python
NTFY_TOPIC = "your-topic-name"
```

You can subscribe via:

- Mobile app (ntfy)
- Web: https://ntfy.sh/your-topic-name

---

### Retry Behavior

Each device is checked:

1. Initial attempt
2. Retry once after a short delay

This helps avoid false alerts from temporary network hiccups.

---

### Timeout Handling

The script uses two layers of timeout:

- SSH `ConnectTimeout` → limits connection time
- Python `subprocess timeout` → hard kill if SSH hangs

This prevents the script from getting stuck indefinitely.

---

### Logging

Logs are written to:

```
~/rpi_ssh_check.log
```

Includes:

- Successful connections
- Failures and error messages
- Retry attempts

---

### Design Notes

- Uses system SSH instead of Python libraries for reliability
- Configuration separated for security and flexibility
- Built with automation and monitoring in mind

---

## 🐛 Troubleshooting

### SSH exits with code 255

- Check IP address
- Ensure device is online
- Verify SSH service is running
- Confirm correct username and key

### Script hangs

- Ensure `timeout` is enabled in `subprocess.run()`

### Permission denied

- Verify SSH key is installed on the Pi
- Confirm correct user is being used

---

## 📄 License

Use freely for personal or internal projects.

---
