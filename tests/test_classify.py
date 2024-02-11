import requests

if __name__ == "__main__":
    response = requests.post("http://127.0.0.1:8000/classify", json={"text": "something about breast cancer"})
    print("Response received:")
    print(response.json())
    response = requests.post("http://127.0.0.1:8000/classify", json={"text": "fig p > 0.1", "label": "partype"})
    print("Response received:")
    print(response.json())
