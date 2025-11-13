# CSWebDriver (Controlled Stealth WebDriver)

A lightweight web API built with **Bottle** and **selenium-stealth** that provides endpoints to interact with web pages while bypassing common scraping detection techniques.

The project uses **uv** for dependency and environment management.

## Overview

CSWebDriver launches a **headless, stealth-enabled Chrome browser** to interact with target websites and extract data such as network requests.  
The service exposes a simple HTTP interface for these automation tasks, enabling integrations with other systems or scripts.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/CSWebDriver.git
cd CSWebDriver

# Create and sync the environment with uv
uv sync
```

This will install all dependencies and set up the environment automatically.

---

## Running the Server

Start the Bottle web server:

```bash
uv run python main.py
```

The server will run on **http://0.0.0.0:5000** by default.

---

## Endpoints

### `POST /get_network_urls`

Collects and returns all **network request URLs** made by a given webpage during a browsing session.

#### Payload

```json
{
    "url": "https://example.com",
    "timeout": 5.0
}
```

- **url**: The site URL to extract network request URLs from.  
- **timeout** *(optional)*: Time (in seconds) to wait after the page loads before collecting URLs. Default: **5.0s**.

#### Response

```json
{
    "urls": [
        "https://example.com/",
        "https://example.com/script.js",
        "https://example.com/image.png"
    ]
}
```

- **urls**: A list of all captured request URLs made by the site.

#### Error

```json
{
    "error": "Invalid request",
    "details": "Missing field: url"
}
```

- **error**: A short description of what went wrong.  
- **details**: More detailed information about the underlying issue (usually the raw exception message).

---
