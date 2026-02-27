import json, logging, os, queue, re, sys, threading, time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import source.utils.params as p


WEBHOOK_ENV = "CGRINDER_DISCORD_WEBHOOK_URL"
THREAD_ENV = "CGRINDER_DISCORD_THREAD_ID"
RUN_TARGET_ENV = "CGRINDER_DISCORD_TOTAL_RUNS"
COMPACT_ENV = "CGRINDER_DISCORD_COMPACT_MODE"
PING_ON_FINISH_ENV = "CGRINDER_DISCORD_PING_ON_FINISH"
PING_ROLE_ENV = "CGRINDER_DISCORD_PING_ROLE_ID"

_MAX_TITLE = 256
_MAX_DESCRIPTION = 4096
_MAX_FIELD_NAME = 256
_MAX_FIELD_VALUE = 1024
_MAX_FIELDS = 25
_MAX_FOOTER = 2048

_RE_FLOOR = re.compile(r"^Floor\s+(\d+)$")
_RE_TEAM = re.compile(r"^Team:\s+(.+)$")
_RE_GROUP = re.compile(r"^Group:\s+(.+)$")
_RE_DIFFICULTY = re.compile(r"^Difficulty:\s+(.+)$")
_RE_PACK = re.compile(r"^Pack:\s+(.+)$")
_RE_ENTERING = re.compile(r"^Entering\s+(.+)$")
_RE_GROUP_VALUE = re.compile(r"^([A-Za-z\.]+)#(\d+)$")

_FOCUS_LABELS = {
    "BURN": "Fire",
    "BLEED": "Bleed",
    "TREMOR": "Tremor",
    "RUPTURE": "Rupture",
    "SINKING": "Sinking",
    "POISE": "Poise",
    "CHARGE": "Charge",
    "SLASH": "Slash",
    "PIERCE": "Pierce",
    "BLUNT": "Blunt",
    "WRATH": "Wrath",
    "LUST": "Lust",
    "SLOTH": "Sloth",
    "GLUT.": "Gluttony",
    "GLOOM": "Gloom",
    "PRIDE": "Pride",
    "ENVY": "Envy"
}


def _trim(text, limit):
    text = str(text)
    return text if len(text) <= limit else text[: max(0, limit - 3)] + "..."


def _to_float(value, fallback=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _warn_local(message):
    try:
        sys.stderr.write(f"[DiscordWebhook] {message}\n")
    except Exception:
        pass


class DiscordWebhookClient:
    def __init__(self, webhook_url, thread_id=None, timeout=4, max_queue=500, max_retries=2):
        self.webhook_url = webhook_url.strip()
        self.thread_id = thread_id
        self.timeout = timeout
        self.max_retries = max_retries
        self._thread_fallback_used = False

        self._queue = queue.Queue(maxsize=max_queue)
        self._stop_event = threading.Event()
        self._state_lock = threading.Lock()
        self._next_allowed_at = 0.0
        self._invalid_window = []
        self._disabled = False
        self._warned_disabled = False

        self._execute_url = self._build_execute_url()
        self._worker = threading.Thread(target=self._run, daemon=True, name="discord-webhook")

    def _build_execute_url(self):
        params = {"wait": "true"}
        if self.thread_id:
            params["thread_id"] = self.thread_id
        separator = "&" if "?" in self.webhook_url else "?"
        return f"{self.webhook_url}{separator}{urlencode(params)}"

    def _fallback_without_thread(self):
        if not self.thread_id or self._thread_fallback_used:
            return False
        self._thread_fallback_used = True
        self.thread_id = None
        self._execute_url = self._build_execute_url()
        _warn_local("Thread ID was rejected by Discord. Retrying without thread_id.")
        return True

    def start(self):
        if not self._worker.is_alive():
            self._worker.start()

    def close(self):
        self._stop_event.set()
        if self._worker.is_alive():
            self._worker.join(timeout=2)

    def disable(self, reason=""):
        with self._state_lock:
            self._disabled = True
        if not self._warned_disabled:
            extra = f" ({reason})" if reason else ""
            _warn_local(f"Webhook disabled{extra}.")
            self._warned_disabled = True

    def is_disabled(self):
        with self._state_lock:
            return self._disabled

    def send(self, payload, priority=False):
        if self.is_disabled():
            return False
        item = {
            "payload": payload,
            "attempt": 0,
            "priority": 0 if priority else 1
        }
        return self._push_item(item)

    def _push_item(self, item):
        try:
            self._queue.put_nowait(item)
            return True
        except queue.Full:
            try:
                dropped = self._queue.get_nowait()
                self._queue.task_done()
                if dropped.get("priority", 1) == 0 and item.get("priority", 1) == 1:
                    try:
                        self._queue.put_nowait(dropped)
                    except queue.Full:
                        pass
                    return False
            except queue.Empty:
                return False
            try:
                self._queue.put_nowait(item)
                return True
            except queue.Full:
                return False

    def _run(self):
        while not self._stop_event.is_set() or not self._queue.empty():
            try:
                item = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            try:
                self._wait_rate_limit()
                should_retry = self._post(item["payload"], item["attempt"])
                if should_retry and not self._stop_event.is_set():
                    item["attempt"] += 1
                    if item["attempt"] <= self.max_retries and not self.is_disabled():
                        self._push_item(item)
            finally:
                self._queue.task_done()

    def _wait_rate_limit(self):
        with self._state_lock:
            wait_for = self._next_allowed_at - time.time()
        if wait_for > 0:
            time.sleep(wait_for)

    def _set_next_allowed(self, seconds):
        if seconds <= 0:
            return
        with self._state_lock:
            self._next_allowed_at = max(self._next_allowed_at, time.time() + seconds)

    def _set_backoff(self, attempt):
        self._set_next_allowed(min(30.0, 2.0 ** (attempt + 1)))

    def _track_invalid(self):
        now = time.time()
        with self._state_lock:
            self._invalid_window.append(now)
            self._invalid_window = [t for t in self._invalid_window if now - t <= 600]
            if len(self._invalid_window) >= 200:
                self._disabled = True
                return True
        return False

    def _parse_retry_after(self, headers, body):
        header_delay = _to_float(headers.get("Retry-After"), 0.0) if headers else 0.0
        if header_delay > 0:
            return header_delay

        if not body:
            return 1.0
        try:
            payload = json.loads(body.decode("utf-8", errors="ignore"))
            return _to_float(payload.get("retry_after"), 1.0)
        except Exception:
            return 1.0

    def _update_bucket_limit(self, headers):
        if not headers:
            return

        remaining = headers.get("X-RateLimit-Remaining")
        reset_after = headers.get("X-RateLimit-Reset-After")
        if remaining == "0" and reset_after:
            self._set_next_allowed(_to_float(reset_after, 0.0))

    def _post(self, payload, attempt):
        request_data = json.dumps(payload).encode("utf-8")
        request = Request(
            self._execute_url,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": f"ChargeGrinder/{p.V} DiscordWebhook"
            },
            method="POST"
        )

        try:
            with urlopen(request, timeout=self.timeout) as response:
                self._update_bucket_limit(response.headers)
            return False
        except HTTPError as err:
            body = b""
            try:
                body = err.read()
            except Exception:
                pass

            status = err.code
            if status in (400, 403, 404) and self._fallback_without_thread():
                return True

            if status in (401, 403):
                self._track_invalid()
                self.disable(f"HTTP {status}")
                return False

            if status == 404:
                self.disable("HTTP 404")
                return False

            if status == 429:
                retry_after = self._parse_retry_after(err.headers, body)
                self._set_next_allowed(retry_after)
                if self._track_invalid():
                    self.disable("too many invalid requests")
                return True

            if 500 <= status <= 599:
                self._set_backoff(attempt)
                return True

            return False
        except URLError:
            self._set_backoff(attempt)
            return True
        except Exception:
            self._set_backoff(attempt)
            return True


class WebhookLogHandler(logging.Handler):
    def __init__(self, client):
        super().__init__(level=logging.INFO)
        self.client = client
        self.client.start()

        self.compact_mode = self._read_bool_env(COMPACT_ENV)
        self.ping_on_finish = self._read_bool_env(PING_ON_FINISH_ENV)
        self.ping_role_id = self._read_ping_role_id()
        self.target_runs = self._read_target_runs()
        self.context = {
            "team": None,
            "group": None,
            "difficulty": None,
            "floor": None,
            "pack": None,
            "runs_done": 0,
            "start_announced": False,
            "script_boot": False
        }
        self.run_started_at = None
        self.floor_started_at = None
        self.room_started_at = None
        self.last_room_duration = None
        self.last_floor_duration = None
        self.last_run_duration = None
        self._last_sent = {}

    def _read_bool_env(self, env_name):
        value = os.environ.get(env_name, "").strip().lower()
        return value in ("1", "true", "yes", "on")

    def _read_ping_role_id(self):
        value = os.environ.get(PING_ROLE_ENV, "").strip()
        return value if value.isdigit() else ""

    def _read_target_runs(self):
        value = os.environ.get(RUN_TARGET_ENV, "").strip()
        if not value:
            return None
        if value.upper() == "ALL":
            return "ALL"
        if value.isdigit():
            return str(int(value))
        return None

    def _refresh_runtime_options(self):
        self.compact_mode = self._read_bool_env(COMPACT_ENV)
        self.ping_on_finish = self._read_bool_env(PING_ON_FINISH_ENV)
        self.ping_role_id = self._read_ping_role_id()
        self.target_runs = self._read_target_runs()

    def _reset_run_timers(self):
        self.run_started_at = None
        self.floor_started_at = None
        self.room_started_at = None
        self.last_room_duration = None
        self.last_floor_duration = None
        self.last_run_duration = None
        self.context["floor"] = None
        self.context["pack"] = None
        self.context["start_announced"] = False

    def _format_duration(self, seconds):
        if seconds is None:
            return None
        total = max(0, int(round(seconds)))
        hours, rem = divmod(total, 3600)
        minutes, sec = divmod(rem, 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{sec:02d}"
        return f"{minutes:02d}:{sec:02d}"

    def _runs_done(self):
        return self.context["runs_done"]

    def _run_progress(self):
        done = self._runs_done()
        if self.target_runs is not None:
            return f"{done}/{self.target_runs}"
        return str(done)

    def _focus_label(self, value):
        if not value:
            return value
        normalized = str(value).strip()
        return _FOCUS_LABELS.get(normalized.upper(), normalized.title() if normalized.isupper() else normalized)

    def _group_label(self, value):
        if not value:
            return value
        raw = str(value).strip()
        match = _RE_GROUP_VALUE.match(raw)
        if not match:
            return raw
        focus_raw, number = match.groups()
        return f"{self._focus_label(focus_raw)}#{number}"

    def _should_ping(self, record, event_name):
        if not self.ping_on_finish or not self.ping_role_id:
            return False
        if record.levelno >= logging.ERROR:
            return True
        if event_name != "Run":
            return False
        if self.target_runs is None or self.target_runs == "ALL":
            return False
        try:
            target = int(self.target_runs)
        except (TypeError, ValueError):
            return False
        return self._runs_done() >= target

    def _make_event(self, name, value, description=None, extra_fields=None):
        return {
            "name": name,
            "value": value,
            "description": description,
            "extra_fields": extra_fields or []
        }

    def _normalize_events(self, event):
        if event is None:
            return []

        items = event if isinstance(event, list) else [event]
        normalized = []
        for item in items:
            if item is None:
                continue
            if isinstance(item, dict):
                name = item.get("name")
                if not name:
                    continue
                normalized.append({
                    "name": str(name),
                    "value": str(item.get("value", "")),
                    "description": item.get("description"),
                    "extra_fields": item.get("extra_fields", [])
                })
                continue

            if isinstance(item, tuple) and len(item) == 2:
                normalized.append({
                    "name": str(item[0]),
                    "value": str(item[1]),
                    "description": None,
                    "extra_fields": []
                })
        return normalized

    def _maybe_run_start_event(self, event_time):
        if self.context["start_announced"]:
            return None
        if not self.context["team"] or not self.context["difficulty"]:
            return None

        focus = self._focus_label(self.context["team"])
        group = self._group_label(self.context["group"]) if self.context["group"] else focus
        run_number = self._runs_done() + 1
        prefix = "Script started. " if self.context["script_boot"] and self._runs_done() == 0 else ""

        self.run_started_at = event_time
        self.floor_started_at = None
        self.room_started_at = None
        self.last_room_duration = None
        self.last_floor_duration = None
        self.last_run_duration = None
        self.context["floor"] = None
        self.context["pack"] = None
        self.context["start_announced"] = True
        self.context["script_boot"] = False
        return self._make_event(
            "Run Start",
            f"Run {run_number}",
            description=(
                f"{prefix}Entered Mirror Dungeon with team {group}, "
                f"focus {focus}. Run {run_number} started."
            )
        )

    def close(self):
        try:
            self.client.close()
        finally:
            super().close()

    def emit(self, record):
        if self.client.is_disabled():
            return

        message = record.getMessage().strip()
        if not message:
            return

        try:
            event = self._parse_event(record.levelno, message, record.created)
            if event is None:
                return

            if self._is_duplicate(record.levelno, message):
                return

            events = self._normalize_events(event)
            for event_data in events:
                payload = self._build_payload(record, message, event_data)
                self.client.send(payload, priority=record.levelno >= logging.ERROR)
                if event_data["name"] == "Run":
                    self._reset_run_timers()
        except Exception:
            self.handleError(record)

    def _is_duplicate(self, level, message):
        if message in ("Run Completed", "Run Failed"):
            return False
        now = time.time()
        window = 2.0 if level >= logging.ERROR else 4.0
        last_time = self._last_sent.get(message)
        self._last_sent[message] = now
        return last_time is not None and (now - last_time) < window

    def _parse_event(self, level, message, event_time):
        now = event_time

        if message == "Script started":
            self._refresh_runtime_options()
            self.context["team"] = None
            self.context["group"] = None
            self.context["difficulty"] = None
            self.context["floor"] = None
            self.context["pack"] = None
            self.context["runs_done"] = 0
            self.context["start_announced"] = False
            self.context["script_boot"] = True
            self._reset_run_timers()
            return None

        match = _RE_TEAM.match(message)
        if match:
            self.context["team"] = match.group(1)
            self.context["group"] = None
            self.context["start_announced"] = False
            return None

        match = _RE_GROUP.match(message)
        if match:
            self.context["group"] = match.group(1)
            return self._maybe_run_start_event(now)

        match = _RE_DIFFICULTY.match(message)
        if match:
            self.context["difficulty"] = match.group(1)
            return self._maybe_run_start_event(now)

        match = _RE_FLOOR.match(message)
        if match:
            floor_value = int(match.group(1))
            previous_floor = self.context["floor"]
            previous_pack = self.context["pack"]
            floor_changed = previous_floor is not None and floor_value != previous_floor

            if floor_changed and self.floor_started_at is not None:
                self.last_floor_duration = max(0.0, now - self.floor_started_at)
            else:
                self.last_floor_duration = None

            self.context["floor"] = floor_value
            self.floor_started_at = now
            self.room_started_at = None
            self.last_room_duration = None
            self.context["pack"] = None

            # Compact mode now means minimal notifications: no floor-level messages.
            if self.compact_mode:
                return None

            if floor_changed:
                return self._make_event(
                    "Floor Cleared",
                    f"Floor {previous_floor}",
                    description=f"Floor {previous_floor} cleared.",
                    extra_fields=[
                        ("Pack Group", previous_pack, False),
                        ("Floor Time", self._format_duration(self.last_floor_duration), True)
                    ]
                )
            return None

        match = _RE_PACK.match(message)
        if match:
            self.context["pack"] = match.group(1)

            if self.compact_mode:
                return None
            if self.context["floor"] is None:
                return None
            return self._make_event(
                "Floor Entered",
                f"Floor {self.context['floor']}",
                description=f"Entered Floor {self.context['floor']} with pack {self.context['pack']}."
            )

        match = _RE_ENTERING.match(message)
        if match:
            if self.room_started_at is not None:
                self.last_room_duration = max(0.0, now - self.room_started_at)
            else:
                self.last_room_duration = None
            self.room_started_at = now
            if self.floor_started_at is None:
                self.floor_started_at = now
            return None

        if message == "Run Completed":
            self.last_run_duration = None if self.run_started_at is None else max(0.0, now - self.run_started_at)
            self.last_floor_duration = None if self.floor_started_at is None else max(0.0, now - self.floor_started_at)
            current_floor = self.context["floor"]
            current_pack = self.context["pack"]
            self.context["runs_done"] += 1
            run_event = self._make_event("Run", f"Completed ({self._run_progress()})", description="Run completed.")
            if not self.compact_mode and current_floor is not None:
                floor_event = self._make_event(
                    "Floor Cleared",
                    f"Floor {current_floor}",
                    description=f"Floor {current_floor} cleared.",
                    extra_fields=[
                        ("Floor Time", self._format_duration(self.last_floor_duration), True)
                    ]
                )
                return [floor_event, run_event]
            return run_event

        if message == "Run Failed":
            self.last_run_duration = None if self.run_started_at is None else max(0.0, now - self.run_started_at)
            self.last_floor_duration = None if self.floor_started_at is None else max(0.0, now - self.floor_started_at)
            current_floor = self.context["floor"]
            current_pack = self.context["pack"]
            self.context["runs_done"] += 1
            run_event = self._make_event(
                "Run",
                f"Defeat - all sinners down ({self._run_progress()})",
                description="Run failed: all selected sinners are dead."
            )
            if not self.compact_mode and current_floor is not None:
                floor_event = self._make_event(
                    "Floor Cleared",
                    f"Floor {current_floor}",
                    description=f"Floor {current_floor} ended by defeat.",
                    extra_fields=[
                        ("Floor Time", self._format_duration(self.last_floor_duration), True)
                    ]
                )
                return [floor_event, run_event]
            return run_event

        if message in ("Execution paused", "Execution resumed"):
            return self._make_event(
                "Execution",
                message.replace("Execution ", "").capitalize(),
                description=message
            )

        if message in ("Server error happened", "We are stuck", "Initialization error", "Termination error"):
            return self._make_event("Issue", message, description=message)

        if message in ("Exp Luxcavation", "Thread Luxcavation", "Done with Luxcavation!"):
            return self._make_event("Lux", message, description=message)

        if level >= logging.ERROR:
            return self._make_event("Error", message, description=message)

        if level >= logging.WARNING:
            return self._make_event("Warning", message, description=message)

        return None

    def _add_field(self, fields, name, value, inline=True):
        if value in (None, ""):
            return
        if len(fields) >= _MAX_FIELDS:
            return
        fields.append({
            "name": _trim(name, _MAX_FIELD_NAME),
            "value": _trim(value, _MAX_FIELD_VALUE),
            "inline": inline
        })

    def _build_payload(self, record, message, event):
        event_name = event["name"]
        event_value = event["value"]

        if record.levelno >= logging.CRITICAL:
            color = 0x8B0000
            title = "ChargeGrinder Critical"
        elif record.levelno >= logging.ERROR:
            color = 0xE74C3C
            title = "ChargeGrinder Alert"
        elif record.levelno >= logging.WARNING:
            color = 0xF39C12
            title = "ChargeGrinder Warning"
        else:
            color = 0x3498DB
            title = "ChargeGrinder Update"

        fields = []
        if event_name == "Run":
            self._add_field(fields, "Status", event_value)
        elif event_name == "Run Start":
            self._add_field(fields, "Run", event_value)
        self._add_field(fields, "Group", self._group_label(self.context["group"]))
        self._add_field(fields, "Focus", self._focus_label(self.context["team"]))
        self._add_field(fields, "Difficulty", self.context["difficulty"])

        if not self.compact_mode:
            if self.context["floor"] is not None:
                self._add_field(fields, "Floor", str(self.context["floor"]))
            if self.context["pack"]:
                self._add_field(fields, "Pack Group", self.context["pack"], inline=False)

        if event_name == "Run":
            self._add_field(fields, "Total Run Time", self._format_duration(self.last_run_duration))
            if not self.compact_mode:
                self._add_field(fields, "Last Floor Time", self._format_duration(self.last_floor_duration))
        elif self.run_started_at is not None:
            self._add_field(fields, "Run Time", self._format_duration(record.created - self.run_started_at))

        for extra in event.get("extra_fields", []):
            if not isinstance(extra, (list, tuple)) or len(extra) < 2:
                continue
            field_name = extra[0]
            field_value = extra[1]
            inline = bool(extra[2]) if len(extra) > 2 else True
            self._add_field(fields, field_name, field_value, inline=inline)

        self._add_field(fields, "Runs Done/Total", self._run_progress())

        now_utc = datetime.fromtimestamp(record.created, timezone.utc)

        embed = {
            "title": _trim(title, _MAX_TITLE),
            "description": _trim(event.get("description") or f"[{record.levelname}] {message}", _MAX_DESCRIPTION),
            "color": color,
            "fields": fields,
            "footer": {"text": _trim(f"v{p.V} | {now_utc.strftime('%Y-%m-%d %H:%M:%S UTC')}", _MAX_FOOTER)}
        }

        payload = {
            "username": "ChargeGrinder",
            "embeds": [embed],
            "allowed_mentions": {"parse": []}
        }
        if self._should_ping(record, event_name):
            payload["content"] = f"<@&{self.ping_role_id}>"
            payload["allowed_mentions"] = {"parse": [], "roles": [self.ping_role_id]}
        return payload


def create_handler_from_env():
    webhook_url = os.environ.get(WEBHOOK_ENV, "").strip()
    if not webhook_url:
        return None, None

    if "/api/webhooks/" not in webhook_url:
        return None, f"{WEBHOOK_ENV} is set but URL format is invalid."

    thread_id = os.environ.get(THREAD_ENV, "").strip() or None

    try:
        client = DiscordWebhookClient(webhook_url=webhook_url, thread_id=thread_id)
        return WebhookLogHandler(client), None
    except Exception as error:
        return None, f"Failed to initialize Discord webhook handler: {error}"
