import requests
import json

# URL của API
BASE_URL = "http://127.0.0.1:8000"

# Mã Pascal để biên dịch
pascal_code = """
program HelloWorld;
begin
  writeln('Hello, world!');
end.
"""

# Bước 1: Biên dịch Pascal
compile_payload = {
    "code": pascal_code,
    "language": "pascal"
}

compile_response = requests.post(f"{BASE_URL}/compile_and_get_b64", json=compile_payload)
compile_result = compile_response.json()

print("Compile Response:", json.dumps(compile_result, indent=4))

if compile_result['error'] == 'no':
    # Bước 2: Chạy code Pascal
    run_payload = {
        "code": compile_result['src_as_b64'],
        "language": "pascal",
        "stdin": ""
    }

    run_response = requests.post(f"{BASE_URL}/run_code", json=run_payload)
    run_result = run_response.json()

    print("Run Response:", json.dumps(run_result, indent=4))
else:
    print("Compilation failed.")