"""
Veo Test Backend - proxies prompts to Kie.ai Veo 3.1 API
"""

import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Veo Test API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KIE_API_KEY = os.environ.get("KIE_API_KEY")
KIE_BASE = "https://api.kie.ai/api/v1/veo"


class GenerateRequest(BaseModel):
    prompt: str
    model: str = "veo3_fast"
    aspect_ratio: str = "16:9"


@app.get("/")
def root():
    return {"status": "ok", "service": "veo-test"}


@app.post("/generate")
async def generate(req: GenerateRequest):
    if not KIE_API_KEY:
        raise HTTPException(500, "KIE_API_KEY not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.post(
                f"{KIE_BASE}/generate",
                headers={
                    "Authorization": f"Bearer {KIE_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "prompt": req.prompt,
                    "model": req.model,
                    "aspect_ratio": req.aspect_ratio,
                    "enableFallback": False,
                    "enableTranslation": True,
                },
            )
        except httpx.RequestError as e:
            raise HTTPException(502, f"Upstream error: {e}")

        if r.status_code != 200:
            raise HTTPException(r.status_code, f"Kie.ai error: {r.text}")

        return r.json()


@app.get("/status/{task_id}")
async def status(task_id: str):
    if not KIE_API_KEY:
        raise HTTPException(500, "KIE_API_KEY not configured")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            r = await client.get(
                f"{KIE_BASE}/record-info",
                headers={"Authorization": f"Bearer {KIE_API_KEY}"},
                params={"taskId": task_id},
            )
        except httpx.RequestError as e:
            raise HTTPException(502, f"Upstream error: {e}")

        if r.status_code != 200:
            raise HTTPException(r.status_code, f"Kie.ai error: {r.text}")

        return r.json()
