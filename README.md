# Domain & SSL Expiry Radar

Check a newline-separated list of hostnames for HTTPS certificate expiry and domain registration expiry. TLS dates come from the live certificate; domain registration dates come from public RDAP data when the registry publishes one.

## Quick start

```bash
python -m venv .venv
python -m pip install -e .
expiry-radar domains.txt --warn-days 30 --json report.json
```

Example `domains.txt`:

```text
example.com
python.org
```

The checker makes network requests to each host on port 443 and to the RDAP service. Registries may omit dates, block queries, or publish only a renewal/grace-period date. A missing date is reported as unavailable, never guessed.

## Learning notes

The project demonstrates TLS wrapping around a socket, UTC-aware date math, a small HTTP JSON client, and graceful per-host errors so one offline domain does not stop the report.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
```

## License

MIT. See [LICENSE](LICENSE).
