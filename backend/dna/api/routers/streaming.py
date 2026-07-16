import asyncio
import json
import logging
import os
import queue
from typing import Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, HTTPException
from fastapi.responses import StreamingResponse
from starlette.websockets import WebSocketState

from dna.api.analysis import run_full_analysis
from dna.remote import is_github_url, get_local_repo_from_github

logger = logging.getLogger("dna.api.streaming")
router = APIRouter(prefix="/v1/analyze", tags=["analysis"])

def validate_repo_path(path: str) -> str:
    if not path:
        raise ValueError("Repository path must not be empty")
    resolved_path = os.path.abspath(path)
    if ".." in path.replace("\\", "/").split("/"):
        raise ValueError("Path traversal not allowed")
    if not os.path.exists(resolved_path):
        raise ValueError(f"Repository path does not exist: {resolved_path}")
    if not os.path.isdir(resolved_path):
        raise ValueError(f"Repository path is not a directory: {resolved_path}")
    return resolved_path

def resolve_path(input_path: str) -> str:
    stripped = input_path.strip()
    if is_github_url(stripped):
        return get_local_repo_from_github(stripped)
    else:
        return validate_repo_path(stripped)

# --- WebSocket Streaming ---
@router.websocket("/ws")
async def websocket_analyze(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket analysis connection accepted")

    loop = asyncio.get_running_loop()
    event_queue = asyncio.Queue()

    # Progress callback that puts events into the asyncio queue safely
    def progress_callback(step_id: str, status: str, percent: int, message: str):
        payload = {
            "type": "progress",
            "step_id": step_id,
            "status": status,
            "percent": percent,
            "message": message
        }
        loop.call_soon_threadsafe(event_queue.put_nowait, payload)

    # Listen for start command
    try:
        data = await websocket.receive_text()
        params = json.loads(data)
        repo_path = params.get("repo_path")
        if not repo_path:
            await websocket.send_json({"type": "error", "message": "Missing 'repo_path' in payload"})
            await websocket.close()
            return
    except Exception as e:
        logger.error("Failed to receive initial WebSocket command: %s", e)
        await websocket.close()
        return

    # Background analysis execution
    async def run_analysis_task():
        try:
            local_path = await asyncio.to_thread(resolve_path, repo_path)
            # Notify start
            loop.call_soon_threadsafe(event_queue.put_nowait, {
                "type": "log", "message": f"Resolved path to {local_path}. Starting engines..."
            })
            
            result = await asyncio.to_thread(run_full_analysis, local_path, progress_callback)
            
            if is_github_url(repo_path):
                result["repository"]["path"] = repo_path
                
            loop.call_soon_threadsafe(event_queue.put_nowait, {
                "type": "complete", "result": result
            })
        except Exception as ex:
            logger.exception("Error during streaming analysis execution")
            loop.call_soon_threadsafe(event_queue.put_nowait, {
                "type": "error", "message": str(ex)
            })

    analysis_fut = asyncio.create_task(run_analysis_task())

    # Forward queue items and keepalive heartbeats to client
    keepalive_task = None
    try:
        async def keepalive():
            while True:
                await asyncio.sleep(5.0)
                if websocket.client_state == WebSocketState.CONNECTED:
                    await websocket.send_json({"type": "heartbeat"})
        
        keepalive_task = asyncio.create_task(keepalive())

        while not analysis_fut.done() or not event_queue.empty():
            try:
                # Wait for next event or check if analysis finished
                event = await asyncio.wait_for(event_queue.get(), timeout=0.1)
                await websocket.send_json(event)
                event_queue.task_done()
                if event["type"] in ("complete", "error"):
                    break
            except asyncio.TimeoutError:
                continue

    except WebSocketDisconnect:
        logger.warning("WebSocket client disconnected during analysis")
    except Exception as e:
        logger.error("Error in WebSocket streaming loop: %s", e)
    finally:
        if keepalive_task:
            keepalive_task.cancel()
        analysis_fut.cancel()
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close()

# --- Server-Sent Events (SSE) Streaming ---
@router.get("/sse")
async def sse_analyze(repo_path: str = Query(..., description="Target repository path or GitHub URL")):
    loop = asyncio.get_running_loop()
    event_queue = asyncio.Queue()

    def progress_callback(step_id: str, status: str, percent: int, message: str):
        payload = {
            "type": "progress",
            "step_id": step_id,
            "status": status,
            "percent": percent,
            "message": message
        }
        loop.call_soon_threadsafe(event_queue.put_nowait, payload)

    async def run_analysis_task():
        try:
            local_path = await asyncio.to_thread(resolve_path, repo_path)
            loop.call_soon_threadsafe(event_queue.put_nowait, {
                "type": "log", "message": f"Resolved path to {local_path}. Starting engines..."
            })
            
            result = await asyncio.to_thread(run_full_analysis, local_path, progress_callback)
            
            if is_github_url(repo_path):
                result["repository"]["path"] = repo_path
                
            loop.call_soon_threadsafe(event_queue.put_nowait, {
                "type": "complete", "result": result
            })
        except Exception as ex:
            logger.exception("Error during SSE analysis execution")
            loop.call_soon_threadsafe(event_queue.put_nowait, {
                "type": "error", "message": str(ex)
            })

    analysis_fut = asyncio.create_task(run_analysis_task())

    async def event_generator():
        try:
            # Send initial connected message
            yield f"data: {json.dumps({'type': 'connected'})}\n\n"
            
            while True:
                try:
                    event = await asyncio.wait_for(event_queue.get(), timeout=5.0)
                    yield f"data: {json.dumps(event)}\n\n"
                    event_queue.task_done()
                    if event["type"] in ("complete", "error"):
                        break
                except TimeoutError:
                    # Heartbeat
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
                except asyncio.TimeoutError:
                    # Fallback for older python
                    yield f"data: {json.dumps({'type': 'heartbeat'})}\n\n"
        except asyncio.CancelledError:
            logger.warning("SSE analysis stream cancelled by client")
            analysis_fut.cancel()
        except Exception as e:
            logger.error("Error generating SSE events: %s", e)
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
