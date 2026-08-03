"""Record targeted public searches for Byte Adder topology material."""

from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urljoin
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) byte-adder-public-audit/1.0"
MAX_RESPONSE = 2 * 1024 * 1024
QUERIES = [
    '"Turing Complete" "Adding Bytes" 103 5',
    '"Turing Complete" "byte_adder" 103 5',
    '"Turing Complete" "byte adder" 91 6',
    '"Turing Complete" "byte adder" 79 7',
    '"Turing Complete" "byte adder" 154 4',
    '"4d 8bit adder"',
    '"FermiEnergy" adder',
    '"Patchouli" "byte adder"',
    '"zagadka m" adder',
    '"Heistenberg99"',
    '"skyoxZ" adder',
    '"realomg" adder',
    'site:github.com "4d 8bit adder"',
    'site:github.com "Turing Complete" "byte_adder"',
    'site:reddit.com/r/TuringComplete "byte adder"',
    'site:steamcommunity.com/app/1444480 "byte adder"',
    '图灵完备 字节加法器 103 5',
    '图灵完备 8位加法器 4延迟',
]
NAMES = ["FermiEnergy", "Patchouli", "zagadka m", "Heistenberg99", "skyoxZ", "realomg"]


def fetch(url: str, accept: str = "text/html,*/*") -> tuple[int, str]:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    with urlopen(request, timeout=20.0) as response:
        raw = response.read(MAX_RESPONSE + 1)
        if len(raw) > MAX_RESPONSE:
            raise ValueError(f"response exceeds {MAX_RESPONSE} bytes")
        charset = response.headers.get_content_charset() or "utf-8"
        return response.status, raw.decode(charset, errors="replace")


def clean(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def bing(query: str) -> dict:
    url = "https://www.bing.com/search?format=rss&q=" + quote_plus(query)
    status, body = fetch(url, "application/rss+xml,application/xml,text/xml")
    root = ET.fromstring(body)
    return {
        "url": url,
        "status": status,
        "results": [
            {
                "title": clean(item.findtext("title", "")),
                "url": item.findtext("link", ""),
                "snippet": clean(item.findtext("description", "")),
            }
            for item in root.findall("./channel/item")[:10]
        ],
    }


class DuckParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.capture: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = set((values.get("class") or "").split())
        if tag == "a" and "result__a" in classes:
            self.current = {"title": "", "url": values.get("href") or "", "snippet": ""}
            self.results.append(self.current)
            self.capture = "title"
        elif self.current is not None and "result__snippet" in classes:
            self.capture = "snippet"

    def handle_endtag(self, tag: str) -> None:
        if tag in {"a", "div"}:
            self.capture = None

    def handle_data(self, data: str) -> None:
        if self.current is not None and self.capture:
            self.current[self.capture] += data


def duck(query: str) -> dict:
    url = "https://html.duckduckgo.com/html/?q=" + quote_plus(query)
    status, body = fetch(url)
    parser = DuckParser()
    parser.feed(body)
    for item in parser.results:
        item["title"] = clean(item["title"])
        item["snippet"] = clean(item["snippet"])
    return {"url": url, "status": status, "results": parser.results[:10]}


def json_fetch(url: str) -> tuple[int, object]:
    status, body = fetch(url, "application/vnd.github+json,application/json")
    return status, json.loads(body)


def github() -> list[dict]:
    calls = []
    searches = []
    for name in NAMES:
        searches.extend([("users", name), ("repositories", f'"{name}" "Turing Complete"'), ("issues", f'"{name}" "Turing Complete"')])
    searches.extend(
        [
            ("repositories", '"Turing Complete" "byte_adder"'),
            ("repositories", '"Turing Complete" adder schematic'),
            ("issues", '"4d 8bit adder"'),
            ("issues", '"Adding Bytes" "Turing Complete"'),
        ]
    )
    for kind, query in searches:
        url = f"https://api.github.com/search/{kind}?per_page=30&q={quote_plus(query)}"
        try:
            status, payload = json_fetch(url)
            items = payload.get("items", []) if isinstance(payload, dict) else []
            calls.append(
                {
                    "kind": kind,
                    "query": query,
                    "url": url,
                    "status": status,
                    "results": [
                        {
                            "name": item.get("full_name") or item.get("login") or item.get("title"),
                            "url": item.get("html_url"),
                            "description": (item.get("description") or item.get("body") or "")[:2000],
                        }
                        for item in items
                    ],
                }
            )
        except Exception as exc:
            calls.append({"kind": kind, "query": query, "url": url, "error": f"{type(exc).__name__}: {exc}"})
        time.sleep(0.2)
    return calls


def reddit() -> list[dict]:
    calls = []
    for query in ["byte adder", "Adding Bytes", "8 bit adder", *NAMES]:
        url = "https://www.reddit.com/r/TuringComplete/search.json?restrict_sr=1&limit=100&q=" + quote_plus(query)
        try:
            status, payload = json_fetch(url)
            children = payload.get("data", {}).get("children", []) if isinstance(payload, dict) else []
            calls.append(
                {
                    "query": query,
                    "url": url,
                    "status": status,
                    "results": [
                        {
                            "title": child.get("data", {}).get("title"),
                            "url": urljoin("https://www.reddit.com", child.get("data", {}).get("permalink", "")),
                            "selftext": child.get("data", {}).get("selftext", "")[:2000],
                        }
                        for child in children
                    ],
                }
            )
        except Exception as exc:
            calls.append({"query": query, "url": url, "error": f"{type(exc).__name__}: {exc}"})
        time.sleep(0.2)
    return calls


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            href = dict(attrs).get("href") or ""
            self.current = {"url": href, "text": ""}
            self.links.append(self.current)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self.current = None

    def handle_data(self, data: str) -> None:
        if self.current is not None:
            self.current["text"] += data


def steam() -> list[dict]:
    calls = []
    for query in ["byte adder", "Adding Bytes", "adder", *NAMES]:
        for kind, url in [
            ("discussions", "https://steamcommunity.com/app/1444480/discussions/search/?q=" + quote_plus(query)),
            ("screenshots", "https://steamcommunity.com/app/1444480/screenshots/?searchText=" + quote_plus(query)),
        ]:
            try:
                status, body = fetch(url)
                parser = LinkParser()
                parser.feed(body)
                seen = set()
                results = []
                for item in parser.links:
                    absolute = urljoin("https://steamcommunity.com", item["url"])
                    label = clean(item["text"])
                    if absolute in seen or not label:
                        continue
                    if "/sharedfiles/filedetails/" in absolute or "/discussions/forum/" in absolute:
                        seen.add(absolute)
                        results.append({"url": absolute, "text": label})
                calls.append({"kind": kind, "query": query, "url": url, "status": status, "results": results[:100]})
            except Exception as exc:
                calls.append({"kind": kind, "query": query, "url": url, "error": f"{type(exc).__name__}: {exc}"})
            time.sleep(0.2)
    return calls


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("public-search.json"))
    args = parser.parse_args()
    result: dict[str, object] = {"queries": QUERIES, "web": []}
    for query in QUERIES:
        entry: dict[str, object] = {"query": query}
        for name, operation in (("bing", bing), ("duckduckgo", duck)):
            try:
                entry[name] = operation(query)
            except (HTTPError, URLError, TimeoutError, ValueError, ET.ParseError) as exc:
                entry[name] = {"error": f"{type(exc).__name__}: {exc}"}
        result["web"].append(entry)  # type: ignore[union-attr]
        time.sleep(0.2)
    result["github"] = github()
    result["reddit"] = reddit()
    result["steam"] = steam()
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
