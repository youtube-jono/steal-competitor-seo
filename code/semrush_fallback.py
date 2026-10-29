"""Semrush through your API key, for when the claude.ai connector can't (out of units, not connected).

Usage:
    python3 code/semrush_fallback.py resource_organic_unique '{"target": "acmeplumbing.com", "database": "us", "display_limit": 20, "display_sort": "traffic_desc"}' --out output/acmeplumbing.com/raw/semrush-top-pages.csv
    python3 code/semrush_fallback.py --schema domain_domains

Same report names and params as the connector (references/semrush.md), sent to
Semrush's MCP server with your key. The key comes from SEMRUSH_API_KEY in the
environment or in .env. Every report call spends units; --schema is free.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENDPOINT = "https://mcp.semrush.com/v1/mcp"
TIMEOUT = 120


def api_key():
    key = os.environ.get("SEMRUSH_API_KEY", "")
    env = Path(__file__).resolve().parent.parent / ".env"
    if not key and env.is_file():
        for line in env.read_text().splitlines():
            if line.startswith("SEMRUSH_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"')
    if not key:
        sys.exit("No SEMRUSH_API_KEY in the environment or .env. See references/setup.md.")
    return key


def post(key, body, session=None):
    headers = {"Authorization": f"Apikey {key}", "Content-Type": "application/json",
               "Accept": "application/json, text/event-stream"}
    if session:
        headers["Mcp-Session-Id"] = session
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.headers.get("Mcp-Session-Id"), resp.read().decode()
    except urllib.error.HTTPError as err:
        sys.exit(f"Semrush answered {err.code}. A 401 means the key is wrong or revoked.")


def result(raw):
    """Pull the JSON-RPC result out of a plain or event-stream reply."""
    for line in raw.splitlines():
        line = line.removeprefix("data: ").strip()
        if line.startswith("{"):
            msg = json.loads(line)
            if "error" in msg:
                sys.exit(f"Semrush error: {msg['error']}")
            if "result" in msg:
                return msg["result"]
    sys.exit("Semrush sent an empty reply.")


def call(tool, arguments):
    key = api_key()
    session, raw = post(key, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
        "protocolVersion": "2025-03-26", "capabilities": {}, "clientInfo": {"name": "steal", "version": "1"}}})
    result(raw)
    post(key, {"jsonrpc": "2.0", "method": "notifications/initialized"}, session)
    _, raw = post(key, {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                        "params": {"name": tool, "arguments": arguments}}, session)
    content = result(raw).get("content", [])
    text = "".join(part.get("text", "") for part in content if part.get("type") == "text")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"data": text}


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("report", nargs="?")
    parser.add_argument("params", nargs="?", help="report params as JSON")
    parser.add_argument("--schema", metavar="REPORT", help="print a report's params (free)")
    parser.add_argument("--out", help="save the CSV here")
    args = parser.parse_args()

    if args.schema:
        print(json.dumps(call("get_report_schema", {"report": args.schema}), indent=1)[:4000])
        return 0
    if not args.report or not args.params:
        parser.print_help()
        return 2
    reply = call("execute_report", {"report": args.report, "params": json.loads(args.params)})
    if "code" in reply and "message" in reply:
        print(f"Semrush: {reply['code']} - {reply['message']}")
        return 1
    data = reply.get("data", "")
    units = reply.get("metadata", {}).get("usage", {}).get("api_units")
    if args.out:
        Path(args.out).write_text(data if data.endswith("\n") else data + "\n")
        print(f"Saved {args.out} ({len(data.splitlines()) - 1} rows, {units} units)")
    else:
        print(data)
        print(f"({units} units)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
