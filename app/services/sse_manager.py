import asyncio
import itertools
import json
import logging


class SSEManager:
    def __init__(self) -> None:
        self._connections: set[asyncio.Queue[dict[str, str]]] = set()
        self._lock = asyncio.Lock()
        self._sequence = itertools.count(1)
        self._logger = logging.getLogger("traffic_incident_api.sse")

    async def connect(self) -> asyncio.Queue[dict[str, str]]:
        queue: asyncio.Queue[dict[str, str]] = asyncio.Queue()
        async with self._lock:
            self._connections.add(queue)
        self._logger.info("sse_client_connected connections=%s", len(self._connections))
        return queue

    async def disconnect(self, queue: asyncio.Queue[dict[str, str]]) -> None:
        async with self._lock:
            self._connections.discard(queue)
        self._logger.info("sse_client_disconnected connections=%s", len(self._connections))

    async def broadcast(self, event_name: str, data: dict) -> None:
        message = {
            "id": str(next(self._sequence)),
            "event": event_name,
            "data": json.dumps(data, ensure_ascii=False),
        }
        async with self._lock:
            queues = list(self._connections)
        self._logger.info("sse_broadcast event=%s connections=%s", event_name, len(queues))

        for queue in queues:
            await queue.put(message)

    async def stream(self, queue: asyncio.Queue[dict[str, str]]):
        while True:
            try:
                message = await asyncio.wait_for(queue.get(), timeout=15)
                yield (
                    f"id: {message['id']}\n"
                    f"event: {message['event']}\n"
                    f"data: {message['data']}\n\n"
                )
            except asyncio.TimeoutError:
                yield ": keep-alive\n\n"
