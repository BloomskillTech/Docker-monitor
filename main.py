import subprocess
import json
from typing import Optional
from fastapi import FastAPI
import uvicorn
from fastapi.responses import FileResponse

app = FastAPI(
    docs_url=None,
    redoc_url=None
)

@app.get("/")
def read_root():
    print("GEt")
    return FileResponse("static/index.html")

@app.get("/docker/id")
def get_docker_id():
    result = subprocess.check_output([
        "docker","ps","-a","--format", "{{.Names}}"
    ]).decode("utf-8").strip().split("\n")
    return (result)

@app.get("/docker/stats")
def get_docker_stats(name: Optional[str] = None):
    try:
        result = subprocess.check_output([
            "docker", "stats", "--no-stream", "--format", "{{json .}}"
        ]).decode("utf-8").strip().split("\n")
        stats = [json.loads(line) for line in result]
        if name:
            for container in stats:
                if container.get("Name") == name:
                    return {"stats": container}
            return {"error": "Container not found"}
        return {"stats": stats}

    except subprocess.CalledProcessError as e:
        return {"error": "Failed to fetch docker stats", "details": str(e)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)