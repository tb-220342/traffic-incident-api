from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/events", tags=["stream"])


@router.get("/stream")
async def stream_events(request: Request):
    sse_manager = request.app.state.sse_manager
    queue = await sse_manager.connect()

    async def event_generator():
        try:
            async for message in sse_manager.stream(queue):
                if await request.is_disconnected():
                    break
                yield message
        finally:
            await sse_manager.disconnect(queue)

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
    }
    return StreamingResponse(event_generator(), media_type="text/event-stream", headers=headers)
