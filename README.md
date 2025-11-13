# ClientHunter CLEAN

ClientHunter CLEAN is a streamlined prospecting and outreach assistant. It combines automated lead discovery with a guided email campaign workflow so you can go from search query to inbox-ready outreach in a few clicks.

## What It Does

- Searches Google for business niches you define and scrapes each hit looking for verified email addresses.
- Stores collected results in timestamped CSV files inside `results/`, ready for review and reuse.
- Provides a Streamlit dashboard (`app.py`) with real-time progress logs, CSV previews, lightweight insights, and campaign controls.
- Sends personalized multi-language email campaigns using templated copy, configurable delays, and Gmail SMTP app passwords.
- Supports safe test sends and ships helper scripts for duplicate prevention and manual testing.

## Tech Stack

- Python 3.10+
- Streamlit for the UI layer
- Pandas for CSV handling and quick metrics
- Requests + BeautifulSoup for HTTP fetching and parsing
- googlesearch-python for SERP discovery
- smtplib / email.mime standard library for transactional delivery
- CSV, JSON, and pathlib utilities for portable file management

## Project Layout

- `app.py` – Streamlit UI orchestrating search, real-time output, previews, and campaign launch.
- `email_finder.py` – Google querying, multi-threaded page crawling, validation, and CSV export.
- `email_sender.py` – SMTP campaign runner with randomized throttling and template rendering.
- `email_template.py` – Localized subjects and HTML/text bodies (Portuguese, English, German by default).
- `config_template.py` – Copy to `config.py` and fill in your Gmail app password; keep credentials out of version control.
- `demo_duplicate_prevention.py` / `DUPLICATE_PREVENTION.md` – Illustrate strategies to avoid recontacting leads.
- `test_duplicate_prevention.py`, `test_stop_functionality.py` – Minimal pytest coverage for critical flows.

## Getting Started

1. **Clone & Prepare**
	```bash
	git clone https://github.com/JoaoMonteiro999/ClientHunter.git
	cd ClientHunter/ClientHunter_CLEAN_Distribution
	python -m venv .venv
	source .venv/bin/activate  # On Windows: .venv\Scripts\activate
	```
2. **Install Dependencies**
	```bash
	pip install -r requirements.txt
	```
3. **Configure Email Credentials**
	- Copy `config_template.py` to `config.py` if the file is missing.
	- Generate a Gmail App Password and update `SENHA_APP` (or use environment variables).

## Run the Dashboard

- Launch via Streamlit:
  ```bash
  streamlit run app.py
  ```
- Or use the platform helpers (`start_clienthunter_mac.command`, `.bat`, `.ps1`, `.sh`) bundled in the repo.

When running, follow the three guided steps: search for leads, inspect CSV output, and send a full or test campaign. All generated CSV files stay under `results/` for future reference.

## Sending Campaigns Safely

- Use the **Test Email** expander to validate templates, deliverability, and localization before mass sends.
- Each production send respects 40-90 second randomized pauses to mimic human pacing and limit provider throttling.
- Update `email_template.py` to tweak copy or add languages; the UI automatically reflects available options.
- The `sent_emails_log.json` file helps you track contacted leads when combined with duplicate-prevention utilities.

## Running Tests

```bash
pytest test_duplicate_prevention.py test_stop_functionality.py
```

## Troubleshooting Tips

- Ensure your Google account allows the googlesearch client (rotate queries if you hit rate limits).
- Confirm the Gmail app password is valid; SMTP authentication errors surface in the Streamlit status logs.
- Delete or archive large CSV files if Streamlit previews feel sluggish.
- Regenerate the virtual environment after dependency updates to avoid stale installs.

## License

Internal tooling – confirm usage terms with the project owner before redistribution.

