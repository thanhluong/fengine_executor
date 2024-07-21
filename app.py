from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

import os, base64

from utils import rand_filename


load_dotenv()
app = FastAPI()


class CompileRequest(BaseModel):
    code: str
    language: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/compile_and_get_b64")
def compile_and_get_b64(request: CompileRequest):
    if request.language == "C++":
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
        content_b64 = base64.b64encode(content_binary).decode()

        os.system(f"rm {src_path} {output_path}")

        return {"b64": content_b64}

    return {"b64": request.code, "lang": request.language, "compiler": os.getenv("COMPILER_CPP")}