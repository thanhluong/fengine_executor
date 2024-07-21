from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

import os, requests

from utils import rand_filename, b64e, b64d


load_dotenv()
app = FastAPI()


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
            return {"error": "compilation error"}

        fd_out = open(output_path, "rb")
        content_binary = fd_out.read()
        fd_out.close()
        content_b64 = b64e(content_binary)

        os.system(f"rm {src_path} {output_path}")

        return {"src_as_b64": content_b64}

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
        "stdin": b64e(request.stdin.encode())
    }
    resp = requests.post(endpoint, json=payload)
    stdout = b64d(resp.json()["stdout"])
    exec_time = float(resp.json()["time"])
    return {"stdout": stdout, "exec_time": exec_time}
