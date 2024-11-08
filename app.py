from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

import os, requests

from utils import rand_filename, b64e, b64d


load_dotenv()
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompileRequest(BaseModel):
    code: str
    language: str


class RunRequest(BaseModel):
    code: str
    language: str
    stdin: str


@app.get("/api")
def read_root():
    return {"Hello": "World"}


@app.post("/api/compile_and_get_b64")
def compile_and_get_b64(request: CompileRequest):
    """
    :param request: raw source code and programming language
    :return: binary code in base64 format
    """
    if request.language == "cpp":
        prefix = rand_filename(length=12)
        src_path = f"{prefix}.cpp"
        output_path = f"{prefix}.out"

        fd_src = open(src_path, "w")
        fd_src.write(request.code)
        fd_src.close()

        status = os.system(f"{os.getenv('COMPILER_CPP')} -DONLINE_JUDGE -Wall -lm -fmax-errors=5 -march=native -s -O2 -std=c++17 -o {output_path} {src_path}")
        if status != 0:
            return {"error": "compilation error", "src_as_b64": ""}

        fd_out = open(output_path, "rb")
        content_binary = fd_out.read()
        fd_out.close()
        content_b64 = b64e(content_binary)

        os.system(f"rm {src_path} {output_path}")

        return {"error": "no", "src_as_b64": content_b64}
    elif request.language == "py":
        return {"error": "no", "src_as_b64": b64e(request.code.encode())}

    return {"b64": request.code, "lang": request.language, "compiler": os.getenv("COMPILER_CPP")}


@app.post("/api/run_code")
def run_code(request: RunRequest):
    """
    :param request: binary code in base64 form and stdin in base64 form
    :return: stdout after execution
    """
    endpoint = f"{os.getenv('JUDGE0_URL')}/submissions/?base64_encoded=true&wait=true"
    language_id = 71 if request.language == "py" else 44
    payload = {
        "language_id": language_id,
        "source_code": request.code,
        "stdin": b64e(request.stdin.encode()),
        "cpu_time_limit": 2,
        "wall_time_limit": 10,
        "memory_limit": 512 * 1000
    }
    resp = requests.post(endpoint, json=payload).json()
    if "status" not in resp:
        return {"status": "judge error", "stdout": "", "exec_time": 0}
    if resp["status"]["id"] != 3:
        return {"status": resp["status"]["description"], "stdout": "", "exec_time": 0}
    output_raw = resp["stdout"]
    if output_raw is None:
        output_raw = ""
    stdout = b64d(output_raw)
    exec_time = float(resp["time"])
    return {"status": resp["status"]["description"], "stdout": stdout, "exec_time": exec_time}
