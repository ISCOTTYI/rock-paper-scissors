import requests

def send_GET(path):
    url = 'http://localhost:8000' + path
    x = requests.get(url)
    print(x)
    print(x.headers)
    print(x.content)

def send_POST():
    url = 'http://localhost:8000'
    d = {
        "x1":200,
        "y1":100,
        "x2":100,
        "y2":300
    }
    x = requests.post(url, json=d)
    print(x)
    print(x.headers)
    print(x.content)

if __name__ == '__main__':
    # send_GET('/init')
    send_GET('/state')
    send_POST()
    send_GET('/state')