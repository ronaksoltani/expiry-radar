import argparse
import json
from pathlib import Path

from .checker import inspect_domain


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check domain and TLS certificate expiry.")
    parser.add_argument("domains_file", type=Path)
    parser.add_argument("--warn-days", type=int, default=30)
    parser.add_argument("--json", type=Path, dest="json_path")
    args = parser.parse_args(argv)
    try:
        domains = [line.strip() for line in args.domains_file.read_text(encoding="utf-8").splitlines()
                   if line.strip() and not line.lstrip().startswith("#")]
    except OSError as error:
        parser.error(str(error))
    results = [inspect_domain(domain) for domain in domains]
    for result in results:
        print(result["domain"])
        for kind in ("tls", "registration"):
            details = result[kind]
            days = details.get("days_remaining")
            status = f"{days} day(s)" if days is not None else details.get("status", "unknown")
            marker = "  ** EXPIRING **" if days is not None and days <= args.warn_days else ""
            print(f"  {kind:12} {status}{marker}")
    if args.json_path:
        args.json_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
