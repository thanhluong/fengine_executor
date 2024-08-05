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
    stdin: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/compile_and_get_b64")
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

        status = os.system(f"{os.getenv('COMPILER_CPP')} -DONLINE_JUDGE -O2 -std=c++17 -o {output_path} {src_path}")
        if status != 0:
            return {"error": "compilation error", "src_as_b64": ""}

        fd_out = open(output_path, "rb")
        content_binary = fd_out.read()
        fd_out.close()
        content_b64 = b64e(content_binary)

        os.system(f"rm {src_path} {output_path}")

        return {"error": "no", "src_as_b64": content_b64}
    elif request.language == "py":
        prefix = rand_filename(length=12)
        src_path = f"{prefix}.py"

        fd_src = open(src_path, "w")
        fd_src.write(request.code)
        fd_src.close()

        status = os.system(f"./venv/bin/pyinstaller {src_path}")
        if status != 0:
            return {"error": "compilation error", "src_as_b64": ""}

        output_path = f"dist/{prefix}/{prefix}"
        fd_out = open(output_path, "rb")
        content_binary = fd_out.read()
        fd_out.close()
        content_b64 = b64e(content_binary)

        os.system(f"rm -rf build dist")
        os.system(f"rm {prefix}.spec {src_path}")

        return {"error": "no", "src_as_b64": content_b64}

    return {"b64": request.code, "lang": request.language, "compiler": os.getenv("COMPILER_CPP")}


@app.post("/run_code")
def run_code(request: RunRequest):
    """
    :param request: binary code in base64 form and stdin in base64 form
    :return: stdout after execution
    """
    endpoint = f"{os.getenv('JUDGE0_URL')}/submissions/?base64_encoded=true&wait=true"
    payload = {
        "language_id": 44,
        "source_code": request.code,
        "stdin": b64e(request.stdin.encode()),
        "cpu_time_limit": 1,
        "wall_time_limit": 10
    }
    resp = requests.post(endpoint, json=payload).json()
    if "status" not in resp:
        return {"status": "judge error", "stdout": "", "exec_time": 0}
    if resp["status"]["id"] != 3:
        return {"status": resp["status"]["description"], "stdout": "", "exec_time": 0}
    stdout = b64d(resp["stdout"])
    exec_time = float(resp["time"])
    return {"status": resp["status"]["description"], "stdout": stdout, "exec_time": exec_time}
