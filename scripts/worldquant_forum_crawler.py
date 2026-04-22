#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import dataclasses
import hashlib
import json
import os
import re
import shutil
import socket
import sqlite3
import struct
import subprocess
import sys
import tempfile
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse


DEFAULT_BROWSER_BINARY = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
DEFAULT_CHROME_ROOT = Path.home() / "Library/Application Support/Google/Chrome"
DEFAULT_CHROME_PROFILE = "Profile 1"
DEFAULT_SEEDS = [
    "https://support.worldquantbrain.com/hc/en-us/community/topics",
    "https://support.worldquantbrain.com/hc/en-us/community/topics/18068926798871-BRAIN-TIPS",
]
DEFAULT_OUTPUT_PARENT = Path("runs/forum-crawl")
DEFAULT_CACHE_PARENT = Path.home() / ".cache/worldquant-forum-crawler"
SUPPORT_HOSTS = {"support.worldquantbrain.com"}
COMMUNITY_PATH_RE = re.compile(r"^/hc/(en-us|zh-cn)/community/")
COMMUNITY_LINK_RE = re.compile(r"^/hc/(en-us|zh-cn)/community/(topics|posts)(/|$)")
PROFILE_COOKIE_HOSTS = ("support.worldquantbrain.com", "worldquantbrain.com", "worldquantbrain.zendesk.com")

FAMILY_RULES = [
    {
        "id": "dataset_evaluation_freshness",
        "label": "Dataset Evaluation / Freshness",
        "scope": "skill",
        "source_terms": [
            "datafield",
            "coverage",
            "frequency",
            "bounds",
            "distribution",
            "long count",
            "short count",
            "update frequency",
        ],
        "transform_terms": ["none neutralization", "decay 0", "ts_std_dev", "abs", "scale_down", "ts_median"],
        "time_terms": ["5", "22", "66", "252", "1000", "week", "month", "quarter", "5 years"],
        "group_terms": ["none", "universe size"],
        "risk_terms": ["missing data", "coverage", "update frequency", "stale"],
        "why": "Reusable field-discovery workflow for checking coverage, freshness, bounds, and distribution before alpha design.",
    },
    {
        "id": "nan_handling_missingness",
        "label": "NaN Handling / Missingness",
        "scope": "skill",
        "source_terms": ["nan", "missing data", "coverage", "non-nan", "group value", "backfill"],
        "transform_terms": ["ts_backfill", "is_nan", "to_nan", "group_max", "if_else", "trade_when"],
        "time_terms": ["on", "off", "group operators", "time series operators"],
        "group_terms": ["group value", "group operator"],
        "risk_terms": ["ambiguity", "volatility", "coverage", "turnover"],
        "why": "Reusable decision rule for handling missing data without destroying signal or coverage.",
    },
    {
        "id": "price_volume_short_horizon",
        "label": "Price / Volume Short Horizon",
        "scope": "kb",
        "source_terms": ["open", "close", "high", "low", "vwap", "volume", "adv20", "sharesout", "price volume"],
        "transform_terms": ["rank", "ts_rank", "ts_delta", "trade_when", "decay", "scale"],
        "time_terms": ["5", "20", "60", "252", "short horizon", "lookback", "short-term"],
        "group_terms": ["industry", "subindustry", "group_rank", "group_neutralize"],
        "risk_terms": ["turnover", "cost", "overfitting", "subuniverse", "test period", "rank test"],
        "why": "Useful for short-horizon momentum/reversal and volume-shock ideas.",
    },
    {
        "id": "fundamental_model_slow_ratio",
        "label": "Fundamental / Model Slow Ratio",
        "scope": "kb",
        "source_terms": [
            "assets",
            "equity",
            "debt",
            "revenue",
            "net income",
            "cash",
            "cashflow",
            "liabilities",
            "liabilities_curr",
            "assets_curr",
            "fnd6_teq",
            "fnd6_ceq",
            "fnd6_pbk",
            "mdl110_score",
            "mdl110_value",
            "mdl_analyst_sentiment",
        ],
        "transform_terms": ["ratio", "rank", "ts_delay", "ts_mean", "backfill", "group_rank"],
        "time_terms": ["63", "84", "126", "252", "504", "quarter", "quarterly", "months"],
        "group_terms": ["industry", "value", "growth", "leverage", "group_rank", "group_neutralize"],
        "risk_terms": ["coverage", "staleness", "subuniverse", "weight", "outlier"],
        "why": "Slow fundamental and model-data signals usually need ratio form and grouping discipline.",
    },
    {
        "id": "sentiment_news_attention",
        "label": "Sentiment / News Attention",
        "scope": "kb",
        "source_terms": ["sentiment", "news", "buzz", "social media", "snt_buzz", "attention"],
        "transform_terms": ["rank", "ts_mean", "ts_delta", "trade_when", "group_rank"],
        "time_terms": ["21", "63", "126", "252", "short horizon", "event"],
        "group_terms": ["industry", "group_rank", "group_neutralize"],
        "risk_terms": ["noise", "turnover", "overfitting", "coverage", "event spike"],
        "why": "Attention shocks can be useful if they are smoothed and validated across windows.",
    },
    {
        "id": "event_trigger_low_turnover",
        "label": "Event Trigger / Low Turnover",
        "scope": "kb",
        "source_terms": ["event", "entry price", "exit trade", "signal", "close_at_event", "low turnover", "trigger"],
        "transform_terms": ["trade_when", "if_else", "rank", "ts_delta", "ts_mean", "ts_sum"],
        "time_terms": ["5", "20", "60", "event", "entry", "exit"],
        "group_terms": ["group_neutralize", "group_rank", "industry"],
        "risk_terms": ["turnover", "stale position", "sparse trigger", "exit"],
        "why": "Template family for event-driven alphas that need explicit entry/exit control and sparse triggers.",
    },
    {
        "id": "options_data_volatility",
        "label": "Options / Volatility",
        "scope": "kb",
        "source_terms": ["options", "implied volatility", "iv", "open interest", "delta", "gamma", "skew"],
        "transform_terms": ["rank", "ts_rank", "ts_mean", "ts_delta", "group_rank"],
        "time_terms": ["5", "20", "60", "252", "event", "short horizon"],
        "group_terms": ["industry", "group_rank", "group_neutralize"],
        "risk_terms": ["coverage", "turnover", "crowding", "overfitting"],
        "why": "Options data often needs tight horizon control and a careful liquidity check.",
    },
    {
        "id": "risk_factors_classification",
        "label": "Alpha and Risk Factors",
        "scope": "kb",
        "source_terms": ["risk factors", "beta", "size", "value", "momentum", "quality", "style factors"],
        "transform_terms": ["rank", "group_rank", "neutralize", "group_neutralize", "ts_rank"],
        "time_terms": ["252", "504", "long horizon", "cross-sectional"],
        "group_terms": ["industry", "style", "factor", "group_rank"],
        "risk_terms": ["correlation", "crowding", "self-correlation", "factor bleed"],
        "why": "Helps distinguish alpha from known risk factor exposure.",
    },
    {
        "id": "statistical_neutralization_overlay",
        "label": "Statistical Neutralization Overlay",
        "scope": "skill",
        "source_terms": ["hidden factors", "common factors", "alpha returns", "residual", "factor structure"],
        "transform_terms": ["neutralization: statistical", "statistical neutralization", "pca", "orthogonal"],
        "time_terms": ["any", "cross-sectional"],
        "group_terms": ["statistical", "pca"],
        "risk_terms": ["correlation", "hidden factor", "common factor", "factor bleed"],
        "why": "Workflow rule for stripping hidden common risk factors from a family.",
    },
    {
        "id": "validation_and_overfitting",
        "label": "Validation / Overfitting Discipline",
        "scope": "skill",
        "source_terms": ["train", "test", "out of sample", "os", "is", "validation"],
        "transform_terms": ["split", "rank test", "multiple test periods", "holdout", "compare"],
        "time_terms": ["80/20", "5 years", "10 years", "longer history", "train/test"],
        "group_terms": ["test period", "subuniverse", "os"],
        "risk_terms": ["overfitting", "false positive", "test period", "submission evidence"],
        "why": "Reusable workflow for deciding whether a family survives holdout checks.",
    },
    {
        "id": "low_parameter_robustness",
        "label": "Low-Parameter Robustness",
        "scope": "skill",
        "source_terms": ["simple", "elegant", "minimal parameters", "few operators", "single dataset"],
        "transform_terms": ["rank", "ts_rank", "simple model", "one lever"],
        "time_terms": ["5", "20", "60", "252", "small perturbation"],
        "group_terms": ["n/a"],
        "risk_terms": ["overfitting", "operator soup", "fragility", "complexity"],
        "why": "Keeps the first batch disciplined and avoids overbuilding a weak thesis.",
    },
]


@dataclass
class BrowserProfileBundle:
    source_root: Path
    source_profile: str
    cache_root: Path
    cache_profile: Path


@dataclass
class CrawlNode:
    url: str
    depth: int
    via: Optional[str] = None
    source: str = "seed"


@dataclass
class PageSnapshot:
    url: str
    final_url: str
    canonical_url: str
    title: str
    kind: str
    depth: int
    via: Optional[str]
    source: str
    fetched_at: str
    html_relpath: str
    text_relpath: str
    meta: Dict[str, Any] = field(default_factory=dict)


class HTMLTextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "article",
        "blockquote",
        "br",
        "div",
        "footer",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "li",
        "p",
        "pre",
        "section",
        "table",
        "tr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: List[str] = []
        self._skip_depth = 0
        self._in_code = False

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            self._skip_depth += 1
            return
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "code":
            self._in_code = True

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"script", "style", "noscript"}:
            if self._skip_depth:
                self._skip_depth -= 1
            return
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "code":
            self._in_code = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = unescape(data)
        if not text:
            return
        self.parts.append(text)

    def get_text(self) -> str:
        raw = "".join(self.parts)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        raw = re.sub(r"[ \t]{2,}", " ", raw)
        return raw.strip()


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def canonicalize_url(url: str) -> str:
    parsed = urlparse(url)
    query_items = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        if key.startswith("utm_"):
            continue
        if key in {"_gl", "ref", "source"}:
            continue
        query_items.append((key, value))
    query = urlencode(query_items, doseq=True)
    return urlunparse((parsed.scheme, parsed.netloc.lower(), parsed.path, parsed.params, query, ""))


def is_support_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.netloc.lower() in SUPPORT_HOSTS and bool(COMMUNITY_PATH_RE.match(parsed.path))


def is_crawlable_community_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.netloc.lower() not in SUPPORT_HOSTS:
        return False
    return bool(COMMUNITY_LINK_RE.match(parsed.path)) or parsed.path.rstrip("/") in {
        "/hc/en-us/community/topics",
        "/hc/zh-cn/community/topics",
    }


def page_kind(url: str) -> str:
    parsed = urlparse(url)
    if re.search(r"/community/posts/", parsed.path):
        return "post"
    if re.search(r"/community/topics/", parsed.path):
        return "topic"
    if parsed.path.rstrip("/") in {"/hc/en-us/community/topics", "/hc/zh-cn/community/topics"}:
        return "topic-index"
    return "page"


def slugify_url(url: str) -> str:
    parsed = urlparse(canonicalize_url(url))
    base = parsed.path.strip("/") or "index"
    base = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-")
    digest = hashlib.sha1(canonicalize_url(url).encode("utf-8")).hexdigest()[:10]
    return f"{base}-{digest}"


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def copy_file(src: Path, dst: Path) -> None:
    ensure_dir(dst.parent)
    shutil.copy2(src, dst)


class ChromeDevToolsClient:
    def __init__(self, host: str, port: int, ws_path: str) -> None:
        self.host = host
        self.port = port
        self.ws_path = ws_path
        self.sock = socket.create_connection((host, port))
        self.sock.settimeout(5.0)
        self.recv_buffer = b""
        self.next_id = 1
        self._handshake()

    def _handshake(self) -> None:
        key = base64.b64encode(os.urandom(16)).decode("ascii")
        request = (
            f"GET {self.ws_path} HTTP/1.1\r\n"
            f"Host: {self.host}:{self.port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {key}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n"
        ).encode("ascii")
        self.sock.sendall(request)
        response = b""
        while b"\r\n\r\n" not in response:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("websocket handshake failed")
            response += chunk
        status_line = response.split(b"\r\n", 1)[0]
        if b"101" not in status_line:
            raise RuntimeError(status_line.decode("utf-8", "replace"))
        _, self.recv_buffer = response.split(b"\r\n\r\n", 1)

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass

    def _send_frame(self, payload: bytes) -> None:
        header = bytearray([0x81])
        length = len(payload)
        if length < 126:
            header.append(0x80 | length)
        elif length < (1 << 16):
            header.append(0x80 | 126)
            header.extend(struct.pack("!H", length))
        else:
            header.append(0x80 | 127)
            header.extend(struct.pack("!Q", length))
        mask = os.urandom(4)
        header.extend(mask)
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
        self.sock.sendall(bytes(header) + masked)

    def _recv_message(self) -> Dict[str, Any]:
        while True:
            while len(self.recv_buffer) < 2:
                self.recv_buffer += self.sock.recv(4096)
            b1 = self.recv_buffer[0]
            b2 = self.recv_buffer[1]
            opcode = b1 & 0x0F
            masked = bool(b2 & 0x80)
            length = b2 & 0x7F
            idx = 2
            if length == 126:
                while len(self.recv_buffer) < idx + 2:
                    self.recv_buffer += self.sock.recv(4096)
                length = struct.unpack("!H", self.recv_buffer[idx : idx + 2])[0]
                idx += 2
            elif length == 127:
                while len(self.recv_buffer) < idx + 8:
                    self.recv_buffer += self.sock.recv(4096)
                length = struct.unpack("!Q", self.recv_buffer[idx : idx + 8])[0]
                idx += 8
            if masked:
                while len(self.recv_buffer) < idx + 4:
                    self.recv_buffer += self.sock.recv(4096)
                mask = self.recv_buffer[idx : idx + 4]
                idx += 4
            else:
                mask = b""
            while len(self.recv_buffer) < idx + length:
                self.recv_buffer += self.sock.recv(4096)
            payload = self.recv_buffer[idx : idx + length]
            self.recv_buffer = self.recv_buffer[idx + length :]
            if opcode == 8:
                raise RuntimeError("websocket closed")
            if opcode != 1:
                continue
            if masked:
                payload = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
            return json.loads(payload.decode("utf-8"))

    def send(self, method: str, params: Optional[Dict[str, Any]] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        msg_id = self.next_id
        self.next_id += 1
        payload: Dict[str, Any] = {"id": msg_id, "method": method}
        if params:
            payload["params"] = params
        if session_id:
            payload["sessionId"] = session_id
        self._send_frame(json.dumps(payload).encode("utf-8"))
        while True:
            message = self._recv_message()
            if message.get("id") != msg_id:
                continue
            if "error" in message:
                raise RuntimeError(message["error"].get("message", str(message["error"])))
            return message.get("result", {})


class ChromeLauncher:
    def __init__(self, browser_binary: Path, profile_bundle: BrowserProfileBundle, headless: bool = False) -> None:
        self.browser_binary = browser_binary
        self.profile_bundle = profile_bundle
        self.headless = headless
        self.process: Optional[subprocess.Popen[str]] = None
        self.port: Optional[int] = None
        self.ws_path: Optional[str] = None

    def launch(self) -> None:
        cache_root = self.profile_bundle.cache_root
        cache_profile = self.profile_bundle.cache_profile
        ensure_dir(cache_root)
        for lock_name in ("SingletonCookie", "SingletonLock", "SingletonSocket", "DevToolsActivePort"):
            lock_path = cache_root / lock_name
            if lock_path.exists():
                lock_path.unlink()
        cmd = [
            str(self.browser_binary),
            f"--user-data-dir={cache_root}",
            f"--profile-directory={self.profile_bundle.source_profile}",
            "--remote-debugging-port=0",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-popup-blocking",
            "--disable-background-networking",
            "--disable-extensions",
            "--disable-sync",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1440,1800",
            "--window-position=2000,0",
        ]
        if self.headless:
            cmd.append("--headless=new")
        cmd.append("about:blank")
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        active_port = cache_root / "DevToolsActivePort"
        for _ in range(300):
            if active_port.exists():
                break
            if self.process.poll() is not None:
                break
            time.sleep(0.1)
        if not active_port.exists():
            raise RuntimeError(f"Chrome did not start cleanly for {cache_root}")
        lines = active_port.read_text(encoding="utf-8").strip().splitlines()
        if len(lines) < 2:
            raise RuntimeError(f"Malformed DevToolsActivePort file at {active_port}")
        self.port = int(lines[0].strip())
        self.ws_path = lines[1].strip()

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.process = None


class ForumCrawler:
    def __init__(self, config: argparse.Namespace) -> None:
        self.config = config
        self.output_root = config.output_root
        self.raw_root = self.output_root / "raw"
        self.pages_root = self.raw_root / "pages"
        self.analysis_root = self.output_root / "analysis"
        self.seen: set[str] = set()
        self.queue: deque[CrawlNode] = deque()
        self.records: List[PageSnapshot] = []
        self.errors: List[Dict[str, Any]] = []
        self.browser_bundle = build_profile_bundle(
            profile_root=config.profile_root,
            profile_directory=config.profile_directory,
            cache_parent=config.cache_parent,
            refresh_profile_copy=config.refresh_profile_copy,
        )
        self.launcher = ChromeLauncher(
            browser_binary=config.browser_binary,
            profile_bundle=self.browser_bundle,
            headless=config.headless,
        )
        self.client: Optional[ChromeDevToolsClient] = None

    def run(self) -> Dict[str, Any]:
        ensure_dir(self.pages_root)
        ensure_dir(self.analysis_root)
        self.launcher.launch()
        assert self.launcher.port is not None and self.launcher.ws_path is not None
        self.client = ChromeDevToolsClient("127.0.0.1", self.launcher.port, self.launcher.ws_path)
        try:
            for seed in self.config.seeds:
                self.queue.append(CrawlNode(url=canonicalize_url(seed), depth=0, source="seed"))
            while self.queue and len(self.records) < self.config.max_pages:
                node = self.queue.popleft()
                canonical = canonicalize_url(node.url)
                if canonical in self.seen:
                    continue
                if not is_crawlable_community_url(canonical):
                    continue
                self.seen.add(canonical)
                try:
                    snapshot = self.visit(node)
                    self.records.append(snapshot)
                except Exception as exc:  # noqa: BLE001
                    error = {
                        "url": node.url,
                        "canonical_url": canonical,
                        "depth": node.depth,
                        "via": node.via,
                        "source": node.source,
                        "error": str(exc),
                    }
                    self.errors.append(error)
                    continue
                if node.depth >= self.config.max_depth:
                    continue
                discovered = self.discover_links(snapshot)
                for child in discovered:
                    if child in self.seen:
                        continue
                    if not is_crawlable_community_url(child):
                        continue
                    self.queue.append(CrawlNode(url=child, depth=node.depth + 1, via=snapshot.final_url, source="discovered"))
            manifest = self.write_manifest()
            if self.config.analyze_after_crawl:
                self.analyze()
            return manifest
        finally:
            self.client = None
            self.launcher.stop()

    def _target_session(self, url: str) -> Tuple[str, str]:
        assert self.client is not None
        target = self.client.send("Target.createTarget", {"url": "about:blank"})
        target_id = target["targetId"]
        session = self.client.send("Target.attachToTarget", {"targetId": target_id, "flatten": True})
        session_id = session["sessionId"]
        self.client.send("Page.enable", session_id=session_id)
        self.client.send("Runtime.enable", session_id=session_id)
        self.client.send("Page.navigate", {"url": url}, session_id=session_id)
        return target_id, session_id

    def _accept_cookie_banner(self, session_id: str) -> None:
        assert self.client is not None
        script = """
        (() => {
          const labels = [/accept all/i, /accept/i, /agree/i];
          const buttons = Array.from(document.querySelectorAll('button'));
          for (const button of buttons) {
            const text = (button.innerText || button.textContent || '').trim();
            if (!text) continue;
            if (labels.some((rx) => rx.test(text))) {
              button.click();
              return text;
            }
          }
          return null;
        })()
        """
        try:
            self.client.send(
                "Runtime.evaluate",
                {"expression": script, "returnByValue": True, "awaitPromise": False},
                session_id=session_id,
            )
        except Exception:
            return

    def _extract_page(self, session_id: str) -> Dict[str, Any]:
        assert self.client is not None
        js = r"""
        (() => {
          const normalize = (value) => (value || '').replace(/\s+/g, ' ').trim();
          const anchors = Array.from(document.querySelectorAll('a[href]')).map((a) => {
            try {
              return {
                text: normalize(a.innerText || a.textContent || ''),
                href: new URL(a.getAttribute('href'), location.href).href,
              };
            } catch (error) {
              return null;
            }
          }).filter(Boolean);
          const seen = new Set();
          const uniqueAnchors = [];
          for (const anchor of anchors) {
            if (!anchor.href) continue;
            if (seen.has(anchor.href)) continue;
            seen.add(anchor.href);
            uniqueAnchors.push(anchor);
          }
          const codeBlocks = Array.from(document.querySelectorAll('pre code, article code, main code, code'))
            .map((el) => normalize(el.innerText || el.textContent || ''))
            .filter(Boolean);
          const uniqueCodes = [];
          const seenCodes = new Set();
          for (const code of codeBlocks) {
            if (seenCodes.has(code)) continue;
            seenCodes.add(code);
            uniqueCodes.push(code);
          }
          const headings = Array.from(document.querySelectorAll('h1,h2,h3'))
            .map((el) => normalize(el.innerText || el.textContent || ''))
            .filter(Boolean);
          return {
            url: location.href,
            title: normalize(document.title || ''),
            readyState: document.readyState,
            html: document.documentElement.outerHTML,
            headings,
            anchors: uniqueAnchors,
            codeBlocks: uniqueCodes,
          };
        })()
        """
        result = self.client.send(
            "Runtime.evaluate",
            {"expression": js, "returnByValue": True, "awaitPromise": False},
            session_id=session_id,
        )
        return result["result"]["value"]

    def visit(self, node: CrawlNode) -> PageSnapshot:
        assert self.client is not None
        target_id, session_id = self._target_session(node.url)
        try:
            data: Dict[str, Any] = {}
            deadline = time.time() + self.config.page_wait_seconds
            while time.time() < deadline:
                time.sleep(self.config.poll_interval)
                self._accept_cookie_banner(session_id)
                data = self._extract_page(session_id)
                if data.get("readyState") == "complete" and data.get("html"):
                    break
            html = data.get("html", "")
            final_url = data.get("url", node.url)
            title = data.get("title", "")
            kind = page_kind(final_url)
            slug = slugify_url(final_url)
            html_relpath = Path("raw") / "pages" / f"{slug}.html"
            text_relpath = Path("raw") / "pages" / f"{slug}.txt"
            json_relpath = Path("raw") / "pages" / f"{slug}.json"
            html_path = self.output_root / html_relpath
            text_path = self.output_root / text_relpath
            json_path = self.output_root / json_relpath
            write_text(html_path, html)
            text = html_to_text(html)
            write_text(text_path, text)
            page_payload = {
                "url": node.url,
                "final_url": final_url,
                "canonical_url": canonicalize_url(final_url),
                "title": title,
                "kind": kind,
                "depth": node.depth,
                "via": node.via,
                "source": node.source,
                "fetched_at": now_iso(),
                "html_path": str(html_relpath.as_posix()),
                "text_path": str(text_relpath.as_posix()),
                "content_excerpt": text[:5000],
                "headings": data.get("headings", []),
                "anchors": data.get("anchors", []),
                "code_blocks": data.get("codeBlocks", []),
                "meta": {
                    "title_length": len(title),
                    "html_length": len(html),
                    "text_length": len(text),
                    "anchor_count": len(data.get("anchors", [])),
                    "code_block_count": len(data.get("codeBlocks", [])),
                },
            }
            write_json(json_path, page_payload)
            return PageSnapshot(
                url=node.url,
                final_url=final_url,
                canonical_url=canonicalize_url(final_url),
                title=title,
                kind=kind,
                depth=node.depth,
                via=node.via,
                source=node.source,
                fetched_at=page_payload["fetched_at"],
                html_relpath=str(html_relpath.as_posix()),
                text_relpath=str(text_relpath.as_posix()),
                meta=page_payload["meta"],
            )
        finally:
            assert self.client is not None
            try:
                self.client.send("Target.closeTarget", {"targetId": target_id})
            except Exception:
                pass

    def discover_links(self, snapshot: PageSnapshot) -> List[str]:
        json_path = self.output_root / snapshot.html_relpath.replace(".html", ".json")
        if not json_path.exists():
            return []
        payload = read_json(json_path)
        links: List[str] = []
        for anchor in payload.get("anchors", []):
            href = anchor.get("href") if isinstance(anchor, dict) else None
            if not href:
                continue
            normalized = canonicalize_url(href)
            if not is_crawlable_community_url(normalized):
                continue
            if normalized == snapshot.canonical_url:
                continue
            links.append(normalized)
        return list(dict.fromkeys(links))

    def write_manifest(self) -> Dict[str, Any]:
        manifest = {
            "generated_at": now_iso(),
            "output_root": str(self.output_root.as_posix()),
            "browser_binary": str(self.config.browser_binary),
            "browser_profile_source_root": str(self.browser_bundle.source_root),
            "browser_profile_source_directory": self.browser_bundle.source_profile,
            "browser_profile_cache_root": str(self.browser_bundle.cache_root),
            "seeds": self.config.seeds,
            "max_pages": self.config.max_pages,
            "max_depth": self.config.max_depth,
            "page_wait_seconds": self.config.page_wait_seconds,
            "poll_interval": self.config.poll_interval,
            "page_count": len(self.records),
            "error_count": len(self.errors),
            "pages": [dataclasses.asdict(record) for record in self.records],
            "errors": self.errors,
        }
        write_json(self.output_root / "crawl-manifest.json", manifest)
        write_text(self.output_root / "README.md", build_run_readme(manifest))
        return manifest

    def analyze(self) -> Dict[str, Any]:
        analyzer = ForumAnalyzer(self.output_root)
        result = analyzer.run()
        return result


class ForumAnalyzer:
    def __init__(self, crawl_root: Path) -> None:
        self.crawl_root = crawl_root
        self.pages_dir = crawl_root / "raw" / "pages"
        self.analysis_dir = crawl_root / "analysis"
        self.page_records: List[Dict[str, Any]] = []
        self.page_texts: Dict[str, str] = {}
        self.page_html: Dict[str, str] = {}
        self.page_text_by_url: Dict[str, str] = {}
        self.page_html_by_url: Dict[str, str] = {}
        self.page_title_by_url: Dict[str, str] = {}
        self.page_meta_by_url: Dict[str, Dict[str, Any]] = {}

    def load_pages(self) -> None:
        for path in sorted(self.pages_dir.glob("*.json")):
            payload = read_json(path)
            self.page_records.append(payload)
            html_path = self.crawl_root / payload["html_path"]
            text_path = self.crawl_root / payload["text_path"]
            html = html_path.read_text(encoding="utf-8", errors="ignore") if html_path.exists() else ""
            text = text_path.read_text(encoding="utf-8", errors="ignore") if text_path.exists() else html_to_text(html)
            url = payload.get("canonical_url") or canonicalize_url(payload.get("final_url") or payload.get("url", ""))
            self.page_html_by_url[url] = html
            self.page_text_by_url[url] = text
            self.page_title_by_url[url] = payload.get("title", "")
            self.page_meta_by_url[url] = payload.get("meta", {})

    def run(self) -> Dict[str, Any]:
        ensure_dir(self.analysis_dir)
        self.load_pages()
        family_catalog = self.build_family_catalog()
        page_matches = self.build_page_matches(family_catalog)
        reports = {
            "generated_at": now_iso(),
            "crawl_root": str(self.crawl_root.as_posix()),
            "page_count": len(self.page_records),
            "families": family_catalog,
            "page_matches": page_matches,
        }
        write_json(self.analysis_dir / "template-catalog.json", reports)
        write_text(self.analysis_dir / "template-catalog.md", render_template_catalog_md(reports))
        write_text(self.analysis_dir / "decision-notes.md", render_decision_notes(reports))
        return reports

    def build_family_catalog(self) -> List[Dict[str, Any]]:
        families: Dict[str, Dict[str, Any]] = {}
        for rule in FAMILY_RULES:
            families[rule["id"]] = {
                "id": rule["id"],
                "label": rule["label"],
                "scope": rule["scope"],
                "why": rule["why"],
                "source_terms": rule["source_terms"],
                "transform_terms": rule["transform_terms"],
                "time_terms": rule["time_terms"],
                "group_terms": rule["group_terms"],
                "risk_terms": rule["risk_terms"],
                "evidence_pages": [],
                "support_count": 0,
                "evidence_score": 0,
                "template": {
                    "information_source": [],
                    "transform": [],
                    "time_window": [],
                    "grouping_or_neutralization": [],
                    "risk_control": [],
                },
                "promotion": "project",
            }
        for payload in self.page_records:
            url = payload.get("canonical_url") or canonicalize_url(payload.get("final_url") or payload.get("url", ""))
            html = self.page_html_by_url.get(url, "")
            text = self.page_text_by_url.get(url, "")
            code_blocks = payload.get("code_blocks", []) or []
            combined = combine_for_search(text, html, code_blocks, payload.get("title", ""))
            for rule in FAMILY_RULES:
                evidence = score_family(rule, combined, code_blocks, payload.get("title", ""))
                if evidence["score"] <= 0:
                    continue
                family = families[rule["id"]]
                family["support_count"] += 1
                family["evidence_score"] += evidence["score"]
                family["evidence_pages"].append(
                    {
                        "url": payload.get("final_url") or payload.get("url"),
                        "title": payload.get("title", ""),
                        "score": evidence["score"],
                        "hits": evidence["hits"],
                        "snippet": evidence["snippet"],
                    }
                )
                for key, values in evidence["template"].items():
                    for value in values:
                        if value not in family["template"][key]:
                            family["template"][key].append(value)
        family_list = sorted(
            families.values(),
            key=lambda item: (scope_rank(item["scope"]), item["support_count"], item["evidence_score"], item["id"]),
            reverse=True,
        )
        for family in family_list:
            family["evidence_pages"] = sorted(family["evidence_pages"], key=lambda item: (item["score"], item["title"]), reverse=True)
            family["template"] = {key: sorted(set(values)) for key, values in family["template"].items()}
            family["promotion"] = recommend_promotion(family)
        return family_list

    def build_page_matches(self, family_catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        matches: List[Dict[str, Any]] = []
        family_lookup = {family["id"]: family for family in family_catalog}
        for payload in self.page_records:
            url = payload.get("canonical_url") or canonicalize_url(payload.get("final_url") or payload.get("url", ""))
            html = self.page_html_by_url.get(url, "")
            text = self.page_text_by_url.get(url, "")
            code_blocks = payload.get("code_blocks", []) or []
            combined = combine_for_search(text, html, code_blocks, payload.get("title", ""))
            page_families: List[Dict[str, Any]] = []
            for rule in FAMILY_RULES:
                evidence = score_family(rule, combined, code_blocks, payload.get("title", ""))
                if evidence["score"] <= 0:
                    continue
                page_families.append(
                    {
                        "family_id": rule["id"],
                        "label": rule["label"],
                        "scope": rule["scope"],
                        "score": evidence["score"],
                        "template": evidence["template"],
                        "hits": evidence["hits"],
                        "support_count": family_lookup[rule["id"]]["support_count"],
                    }
                )
            page_families.sort(key=lambda item: (item["score"], item["scope"], item["family_id"]), reverse=True)
            matches.append(
                {
                    "url": payload.get("final_url") or payload.get("url"),
                    "title": payload.get("title", ""),
                    "kind": payload.get("kind", "page"),
                    "page_score": sum(item["score"] for item in page_families),
                    "families": page_families,
                }
            )
        return matches


def combine_for_search(text: str, html: str, code_blocks: Sequence[str], title: str) -> str:
    pieces = [title or "", text or "", html or "", " ".join(code_blocks or [])]
    return normalize_whitespace(" ".join(pieces).lower())


def keyword_hits(text: str, terms: Sequence[str]) -> List[str]:
    hits: List[str] = []
    for term in terms:
        normalized = term.lower()
        if normalized in text:
            hits.append(term)
    return hits


def regex_hits(text: str, patterns: Sequence[str]) -> List[str]:
    hits: List[str] = []
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            hits.append(pattern)
    return hits


def score_family(rule: Dict[str, Any], text: str, code_blocks: Sequence[str], title: str) -> Dict[str, Any]:
    combined = text
    source_hits = keyword_hits(combined, rule["source_terms"])
    transform_hits = keyword_hits(combined, rule["transform_terms"])
    time_hits = keyword_hits(combined, rule["time_terms"])
    group_hits = keyword_hits(combined, rule["group_terms"])
    risk_hits = keyword_hits(combined, rule["risk_terms"])
    code_hits = [code for code in code_blocks if any(term.lower() in code.lower() for term in rule["transform_terms"])]
    score = len(source_hits) * 3 + len(transform_hits) * 3 + len(time_hits) * 2 + len(group_hits) * 2 + len(risk_hits)
    if code_hits:
        score += 2
    if title and rule["label"].lower().split(" / ")[0] in title.lower():
        score += 1
    template = {
        "information_source": source_hits,
        "transform": transform_hits + (["code"] if code_hits else []),
        "time_window": time_hits,
        "grouping_or_neutralization": group_hits,
        "risk_control": risk_hits,
    }
    snippet = extract_snippet(combined, source_hits + transform_hits + time_hits + group_hits + risk_hits)
    return {
        "score": score,
        "hits": {
            "source": source_hits,
            "transform": transform_hits,
            "time": time_hits,
            "group": group_hits,
            "risk": risk_hits,
            "code": code_hits[:3],
        },
        "template": template,
        "snippet": snippet,
    }


def extract_snippet(text: str, hits: Sequence[str], width: int = 220) -> str:
    if not hits:
        return text[:width]
    index = min((text.lower().find(hit.lower()) for hit in hits if hit), default=0)
    if index < 0:
        index = 0
    start = max(0, index - width // 2)
    end = min(len(text), start + width)
    return text[start:end]


def scope_rank(scope: str) -> int:
    return {"skill": 3, "kb": 2, "project": 1}.get(scope, 0)


def recommend_promotion(family: Dict[str, Any]) -> str:
    scope = family["scope"]
    support_count = family["support_count"]
    if scope == "skill" and support_count >= 1:
        return "skill-candidate"
    if scope == "kb" and support_count >= 1:
        return "kb-candidate"
    return "project"


def render_template_catalog_md(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# WorldQuant Forum Template Catalog")
    lines.append("")
    lines.append(f"- Generated at: `{report['generated_at']}`")
    lines.append(f"- Crawl root: `{report['crawl_root']}`")
    lines.append(f"- Pages crawled: `{report['page_count']}`")
    lines.append("")
    lines.append("## Family Summary")
    lines.append("")
    lines.append("| family | scope | support | promotion | source | transform | time | group / neutralization | risk |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for family in report["families"]:
        tpl = family["template"]
        lines.append(
            "| {label} | {scope} | {support} | {promotion} | {source} | {transform} | {time} | {group} | {risk} |".format(
                label=escape_md(family["label"]),
                scope=family["scope"],
                support=family["support_count"],
                promotion=family["promotion"],
                source=escape_md(join_display(tpl["information_source"])),
                transform=escape_md(join_display(tpl["transform"])),
                time=escape_md(join_display(tpl["time_window"])),
                group=escape_md(join_display(tpl["grouping_or_neutralization"])),
                risk=escape_md(join_display(tpl["risk_control"])),
            )
        )
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    for family in report["families"]:
        lines.append(f"- **{family['label']}** -> `{family['promotion']}`. {family['why']}")
        if family["evidence_pages"]:
            top = family["evidence_pages"][0]
            lines.append(f"  - Top evidence: `{top['title']}` ({top['url']})")
    lines.append("")
    lines.append("## Page Matches")
    lines.append("")
    for page in report["page_matches"]:
        lines.append(f"- `{page['title']}`")
        lines.append(f"  - URL: `{page['url']}`")
        if page["families"]:
            family_bits = []
            for fam in page["families"][:4]:
                family_bits.append(f"{fam['label']} ({fam['score']})")
            lines.append(f"  - Matched: {', '.join(family_bits)}")
    return "\n".join(lines) + "\n"


def render_decision_notes(report: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Forum Crawl Decision Notes")
    lines.append("")
    lines.append("## Suggested Next Step")
    lines.append("")
    for family in report["families"]:
        if family["promotion"] == "skill-candidate":
            lines.append(f"- Promote `{family['label']}` as a `skill-candidate`.")
        elif family["promotion"] == "kb-candidate":
            lines.append(f"- Promote `{family['label']}` as a `kb-candidate`.")
    if not any(f["promotion"] in {"skill-candidate", "kb-candidate"} for f in report["families"]):
        lines.append("- Keep the extracted material project-local for now.")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- Page-specific formulas stay project-local until the family proves reusable.")
    lines.append("- Workflow rules about validation, neutralization, and parameter discipline are the strongest skill candidates.")
    lines.append("- Data-family heuristics around price/volume, fundamentals, sentiment, options, and risk factors are better KB candidates than skill edits.")
    return "\n".join(lines) + "\n"


def join_display(values: Sequence[str]) -> str:
    if not values:
        return "-"
    return ", ".join(values)


def escape_md(text: str) -> str:
    return text.replace("|", "\\|")


def html_to_text(html: str) -> str:
    parser = HTMLTextExtractor()
    parser.feed(html)
    parser.close()
    return parser.get_text()


def detect_profile_directory(chrome_root: Path) -> str:
    candidates = [chrome_root / "Default", chrome_root / DEFAULT_CHROME_PROFILE, chrome_root / "Profile 2", chrome_root / "Profile 3"]
    for child in sorted(chrome_root.glob("Profile *")):
        if child not in candidates:
            candidates.append(child)
    for candidate in candidates:
        cookies = candidate / "Cookies"
        if not cookies.exists():
            continue
        if profile_has_worldquant_cookie(cookies):
            return candidate.name
    raise RuntimeError(f"No Chrome profile with WorldQuant cookies found under {chrome_root}")


def profile_has_worldquant_cookie(cookies_path: Path) -> bool:
    try:
        conn = sqlite3.connect(f"file:{cookies_path}?mode=ro", uri=True, timeout=1.0)
    except sqlite3.Error:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            """
            select 1
            from cookies
            where host_key like '%worldquantbrain.com%'
               or host_key like '%worldquantbrain.zendesk.com%'
               or host_key like '%support.worldquantbrain.com%'
            limit 1
            """
        )
        return cur.fetchone() is not None
    except sqlite3.Error:
        return False
    finally:
        conn.close()


def build_profile_bundle(profile_root: Path, profile_directory: Optional[str], cache_parent: Path, refresh_profile_copy: bool) -> BrowserProfileBundle:
    if profile_directory is None:
        profile_directory = detect_profile_directory(profile_root)
    source_profile_dir = profile_root / profile_directory
    if not source_profile_dir.exists():
        raise RuntimeError(f"Chrome profile directory not found: {source_profile_dir}")
    ensure_dir(cache_parent)
    cache_root = cache_parent / f"{profile_directory.replace(' ', '_')}-bundle"
    cache_profile = cache_root / profile_directory
    if refresh_profile_copy and cache_root.exists():
        shutil.rmtree(cache_root)
    if not cache_root.exists():
        ensure_dir(cache_root)
        source_local_state = profile_root / "Local State"
        if not source_local_state.exists():
            raise RuntimeError(f"Chrome Local State file not found: {source_local_state}")
        copy_file(source_local_state, cache_root / "Local State")
        shutil.copytree(source_profile_dir, cache_profile)
        for lock_name in ("SingletonCookie", "SingletonLock", "SingletonSocket", "DevToolsActivePort"):
            lock_path = cache_profile / lock_name
            if lock_path.exists():
                lock_path.unlink()
    else:
        ensure_dir(cache_profile)
    return BrowserProfileBundle(
        source_root=profile_root,
        source_profile=profile_directory,
        cache_root=cache_root,
        cache_profile=cache_profile,
    )


def build_run_readme(manifest: Dict[str, Any]) -> str:
    lines = []
    lines.append("# Forum Crawl Run")
    lines.append("")
    lines.append("## Metadata")
    lines.append("")
    lines.append(f"- Generated at: `{manifest['generated_at']}`")
    lines.append(f"- Pages crawled: `{manifest['page_count']}`")
    lines.append(f"- Errors: `{manifest['error_count']}`")
    lines.append("")
    lines.append("## Seeds")
    lines.append("")
    for seed in manifest.get("seeds", []):
        lines.append(f"- `{seed}`")
    lines.append("")
    lines.append("## Layout")
    lines.append("")
    lines.append("- `raw/pages/*.json`: per-page crawl metadata")
    lines.append("- `raw/pages/*.html`: rendered page HTML")
    lines.append("- `raw/pages/*.txt`: HTML-stripped text snapshot")
    lines.append("- `analysis/template-catalog.json`: family catalog and page matches")
    lines.append("- `analysis/template-catalog.md`: human-readable summary")
    lines.append("- `analysis/decision-notes.md`: promotion posture and next-step notes")
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Crawl and analyze the public WorldQuant BRAIN support forum using Chrome CDP.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    crawl = subparsers.add_parser("crawl", help="Crawl support forum pages and save raw artifacts")
    crawl.add_argument("--seed", action="append", default=[], help="Seed URL to start from (repeatable)")
    crawl.add_argument("--max-pages", type=int, default=100, help="Maximum number of pages to crawl")
    crawl.add_argument("--max-depth", type=int, default=2, help="Maximum link depth from the seed URLs")
    crawl.add_argument("--page-wait-seconds", type=int, default=20, help="Maximum seconds to wait per page")
    crawl.add_argument("--poll-interval", type=float, default=1.0, help="Polling interval while waiting for a page")
    crawl.add_argument("--browser-binary", type=Path, default=DEFAULT_BROWSER_BINARY, help="Chrome binary path")
    crawl.add_argument("--profile-root", type=Path, default=DEFAULT_CHROME_ROOT, help="Chrome user data root to copy from")
    crawl.add_argument("--profile-directory", help="Chrome profile directory to use; auto-detected if omitted")
    crawl.add_argument("--cache-parent", type=Path, default=DEFAULT_CACHE_PARENT, help="Cache directory for copied profile bundles")
    crawl.add_argument("--output-root", type=Path, default=None, help="Run output root; defaults to a dated runs/forum-crawl folder")
    crawl.add_argument("--refresh-profile-copy", action="store_true", help="Rebuild the copied browser profile bundle")
    crawl.add_argument("--headless", action="store_true", help="Run Chrome headless (often blocked by Cloudflare)")
    crawl.add_argument("--analyze-after-crawl", action="store_true", help="Run the analyzer after the crawl finishes")

    analyze = subparsers.add_parser("analyze", help="Analyze a finished crawl root")
    analyze.add_argument("--crawl-root", type=Path, required=True, help="Path to a crawl run root")

    pipeline = subparsers.add_parser("pipeline", help="Crawl and analyze in one step")
    for action in (pipeline,):
        action.add_argument("--seed", action="append", default=[], help="Seed URL to start from (repeatable)")
        action.add_argument("--max-pages", type=int, default=100, help="Maximum number of pages to crawl")
        action.add_argument("--max-depth", type=int, default=2, help="Maximum link depth from the seed URLs")
        action.add_argument("--page-wait-seconds", type=int, default=20, help="Maximum seconds to wait per page")
        action.add_argument("--poll-interval", type=float, default=1.0, help="Polling interval while waiting for a page")
        action.add_argument("--browser-binary", type=Path, default=DEFAULT_BROWSER_BINARY, help="Chrome binary path")
        action.add_argument("--profile-root", type=Path, default=DEFAULT_CHROME_ROOT, help="Chrome user data root to copy from")
        action.add_argument("--profile-directory", help="Chrome profile directory to use; auto-detected if omitted")
        action.add_argument("--cache-parent", type=Path, default=DEFAULT_CACHE_PARENT, help="Cache directory for copied profile bundles")
        action.add_argument("--output-root", type=Path, default=None, help="Run output root; defaults to a dated runs/forum-crawl folder")
        action.add_argument("--refresh-profile-copy", action="store_true", help="Rebuild the copied browser profile bundle")
        action.add_argument("--headless", action="store_true", help="Run Chrome headless (often blocked by Cloudflare)")
        action.add_argument("--analyze-after-crawl", action="store_true", default=True, help="Run analysis after crawling")

    return parser


def resolve_output_root(output_root: Optional[Path]) -> Path:
    if output_root is not None:
        return output_root
    date_prefix = time.strftime("%Y-%m-%d")
    return DEFAULT_OUTPUT_PARENT / f"{date_prefix}-support-worldquantbrain"


def run_crawl(args: argparse.Namespace) -> Dict[str, Any]:
    output_root = resolve_output_root(args.output_root)
    ensure_dir(output_root)
    crawl_args = argparse.Namespace(**vars(args))
    crawl_args.output_root = output_root
    if not crawl_args.seed:
        crawl_args.seed = list(DEFAULT_SEEDS)
    crawl_args.seeds = list(crawl_args.seed)
    crawler = ForumCrawler(crawl_args)
    return crawler.run()


def run_analysis(crawl_root: Path) -> Dict[str, Any]:
    analyzer = ForumAnalyzer(crawl_root)
    return analyzer.run()


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command in {"crawl", "pipeline"}:
        if args.output_root is None:
            args.output_root = resolve_output_root(None)
        if not args.seed:
            args.seed = list(DEFAULT_SEEDS)
        args.seeds = list(args.seed)
    if args.command == "crawl":
        result = run_crawl(args)
        print(json.dumps({"crawl_root": result["output_root"], "page_count": result["page_count"], "error_count": result["error_count"]}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "analyze":
        result = run_analysis(args.crawl_root)
        print(json.dumps({"crawl_root": result["crawl_root"], "page_count": result["page_count"]}, ensure_ascii=False, indent=2))
        return 0
    if args.command == "pipeline":
        output_root = resolve_output_root(args.output_root)
        ensure_dir(output_root)
        args.output_root = output_root
        result = run_crawl(args)
        if not args.analyze_after_crawl:
            print(json.dumps({"crawl_root": result["output_root"], "page_count": result["page_count"], "error_count": result["error_count"]}, ensure_ascii=False, indent=2))
            return 0
        analysis = run_analysis(output_root)
        print(json.dumps({"crawl_root": result["output_root"], "page_count": result["page_count"], "families": len(analysis["families"])}, ensure_ascii=False, indent=2))
        return 0
    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
