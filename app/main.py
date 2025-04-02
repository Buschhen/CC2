from flask import Flask
import requests

app = Flask(__name__)

def get_vm_name():
    try:
        url = "http://169.254.169.254/metadata/instance?api-version=2021-02-01"
        headers = {"Metadata": "true"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()["compute"]["name"]
    except:
        return "Unknown VM"

@app.route("/")
def home():
    # vm_name = get_vm_name()
    return f"<h1>Hello from VM: test</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
