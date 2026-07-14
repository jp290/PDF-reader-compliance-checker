# PDF Reader Compliance Checker

A prototype agent that checks an organic-food certificate PDF against an import rule: **not expired**, **target product listed**. It rasterizes the certificate's first page, sends it to Gemini 2.5 Flash with a QA-manager prompt, and returns a JSON verdict (`cert_number`, `expiry_date`, `is_expired`, `product_found`, `compliance_status`, `summary`).

**Quickstart:**
```sh
pip install -r requirements.txt
```
Poppler is a system dependency (not pip-installable) — `pdf2image` shells out to it:
```sh
brew install poppler        # macOS
apt-get install poppler-utils   # Debian/Ubuntu
```
Set your key in a `.env` file in the project root:
```
GOOGLE_API_KEY=your-key-here
```
Then run:
```sh
python agent.py path/to/certificate.pdf "Organic Chia Seeds"
```
The target product argument is optional — it defaults to `"Organic Chia Seeds"`.

## Known limits

- Reads only the certificate's first page — a later-page product scope reads as "not found"
- No text-layer extraction — always goes through the vision model, even on a PDF with real embedded text
- JSON parsing is a plain string split on a ` ```json ` fence; a response without one fails to parse
- No retry/error handling around the Gemini call, no test suite
- Hardcoded to one scenario (German bio-food importer) — not generalized to other cert formats

## Origin

First public prototype (created 2026-06-24) — this author's earliest public repo, predating [sharpen](https://github.com/jp290/sharpen), [claude-deck](https://github.com/jp290/claude-deck), and [claude-fleet](https://github.com/jp290/claude-fleet). Not in production use.
