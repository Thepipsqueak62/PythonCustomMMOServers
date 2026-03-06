# Server/WorldServiceDaemon/events.py
import asyncio
import json
from pathlib import Path
from datetime import datetime, time as dt_time, timedelta

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from time import time as timestamp

from PythonProject.WebsocketMMO.Server.common import messagepack_utils
from PythonProject.WebsocketMMO.Server.common.packet_types import EPacketOpcode


class GlobalEventScheduler:
    """
    Schedules global events from JSON file with:
    - Millisecond-precision timing
    - Safe removal of one-time events
    - Hot-reload using async lock to prevent race conditions
    """

    def __init__(self, json_file="events.json"):
        self.servers = set()                  # connected WorldServers
        self.events = []                      # list of event dicts
        self.json_file = Path(json_file)      # JSON file path
        self._reload_lock = asyncio.Lock()    # async lock for safe hot-reload
        self.loop = None                      # will hold main asyncio loop

    async def load_events(self):
        """Load events from JSON file."""
        if not self.json_file.exists():
            print(f"[GlobalEventScheduler] JSON file not found: {self.json_file}")
            return

        try:
            with open(self.json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[GlobalEventScheduler] Failed to load JSON: {e}")
            return

        new_events = []
        now = datetime.now()
        for e in data:
            # Convert "HH:MM" to datetime.time
            event_time_str = e.get("time", "00:00")
            hour, minute = map(int, event_time_str.split(":"))
            event_time = dt_time(hour, minute)
            # Compute next trigger datetime
            next_trigger = datetime.combine(now.date(), event_time)
            if next_trigger < now:
                next_trigger += timedelta(days=1)

            new_events.append({
                "time": event_time,
                "next_trigger": next_trigger,
                "payload": e.get("payload", ""),
                "repeat_daily": bool(e.get("repeat", False)),
            })

        self.events = new_events
        print(f"[GlobalEventScheduler] Loaded {len(self.events)} events from JSON.")

    def add_server(self, websocket):
        self.servers.add(websocket)

    def remove_server(self, websocket):
        self.servers.discard(websocket)

    async def broadcast(self, payload):
        """Send packet to all connected WorldServers."""
        packet = messagepack_utils.pack_packet(EPacketOpcode.WORLD_EVENT, payload=payload)
        for ws in list(self.servers):
            try:
                await ws.send(packet)
            except Exception:
                self.servers.discard(ws)
        print(f"[GlobalEventScheduler] Broadcasted global event at {datetime.now().isoformat()}: {payload}")

    async def _run_scheduler(self):
        """Main scheduler loop with millisecond precision."""
        while True:
            if not self.events:
                await asyncio.sleep(0.05)
                continue

            now = datetime.now()
            next_events = []

            for event in self.events:
                if now >= event["next_trigger"]:
                    await self.broadcast(event["payload"])
                    if event["repeat_daily"]:
                        event["next_trigger"] += timedelta(days=1)
                        next_events.append(event)
                    # one-time events are skipped
                else:
                    next_events.append(event)

            self.events = next_events

            # sleep until the soonest next trigger
            if self.events:
                soonest_trigger = min(e["next_trigger"] for e in self.events)
                sleep_seconds = max((soonest_trigger - datetime.now()).total_seconds(), 0.01)
            else:
                sleep_seconds = 0.05

            await asyncio.sleep(sleep_seconds)

    async def request_reload(self):
        """Reload events safely with async lock."""
        async with self._reload_lock:
            await self.load_events()

    async def start(self):
        """Start scheduler with JSON hot-reload."""
        self.loop = asyncio.get_running_loop()  # store main loop
        await self.load_events()
        self._start_file_watcher()
        await self._run_scheduler()

    def _start_file_watcher(self):
        """Watch JSON file for changes using watchdog with async-safe reload."""

        class ReloadHandler(FileSystemEventHandler):
            def __init__(self, scheduler):
                self.scheduler = scheduler
                self._last_reload = 0

            def on_modified(self, event):
                if event.src_path.endswith(self.scheduler.json_file.name):
                    now_ts = timestamp()
                    if now_ts - self._last_reload > 0.5:  # 500ms debounce
                        print(f"[GlobalEventScheduler] Detected JSON change, reloading events...")
                        # Schedule reload safely in main loop
                        self.scheduler.loop.call_soon_threadsafe(
                            lambda: asyncio.create_task(self.scheduler.request_reload())
                        )
                        self._last_reload = now_ts

        observer = Observer()
        observer.schedule(ReloadHandler(self), path=str(self.json_file.parent), recursive=False)
        observer.start()