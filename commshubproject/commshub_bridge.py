from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.sender import _send_via_applescript

# Mirrors allow_list.yaml — update both if contacts change.
# Stored as lowercase; incoming handles are normalised with .lower() before lookup.
ALLOW_LIST = {"molly.dougall@icloud.com", "drarvinddougall@gmail.com", "gunner.lucy@gmail.com", "nishantdougall@gmail.com", "nishant.dougall@icloud.com"}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # local bridge only — file:// origin is null origin
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class SendRequest(BaseModel):
    recipient: str = ""  # accepted for artifact compatibility, unused
    handle: str = ""
    message: str = ""
    mode: str = ""  # accepted for artifact compatibility, unused


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/send-message")
def send_message(req: SendRequest):
    handle = req.handle.strip()
    message = req.message.strip()
    if not handle:
        return JSONResponse(status_code=400, content={"ok": False, "error": "handle is required"})
    if not message:
        return JSONResponse(status_code=400, content={"ok": False, "error": "message is required"})
    if handle.lower() not in ALLOW_LIST:
        return JSONResponse(status_code=400, content={"ok": False, "error": "handle not in allow-list"})
    try:
        _send_via_applescript(handle, message)
        return {"ok": True}
    except RuntimeError as e:
        return JSONResponse(status_code=500, content={"ok": False, "error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("commshub_bridge:app", host="127.0.0.1", port=8765, reload=False)
