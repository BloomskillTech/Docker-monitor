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

        # Fetch container running time
        container_names = subprocess.check_output([
            "docker", "ps", "-a", "--format", "{{.Names}}"
        ]).decode("utf-8").strip().split("\n")
        if container_names:
            inspect_result = subprocess.check_output([
                "docker", "inspect", "--format", "{{.Name}} {{.State.StartedAt}}"
            ] + container_names).decode("utf-8").strip().split("\n")
            running_times = {
                line.split()[0].strip("/"): line.split()[1] for line in inspect_result
            }
        else:
            running_times = {}

        for container in stats:
            container_name = container.get("Name")
            if container_name in running_times:
                container["uptime"] = running_times[container_name]

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