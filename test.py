import requests

# Define the URL for the compile endpoint
url = "http://127.0.0.1:8000/compile_and_get_b64"

# Define the Python source code to be compiled
source_code = """
def main():
    return "Hello, World!"

if _name_ == "_main_":
    print(main())
"""

# Create the request payload
payload = {
    "code": source_code,
    "language": "py"
}

# Send the request to the compile endpoint
response = requests.post(url, json=payload)

print("Status code:", response.status_code)
if response.status_code == 200:
    try:
        print(response.json())
    except ValueError:
        print("Response content is not valid JSON:")
        print(response.text)
else:
    print("Request failed with status code:", response.status_code)
    print("Response content:", response.text)