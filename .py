import httpx

API_KEY = "sk-4ae1d76e4f0542dcad774d9b41bde234"
resp = httpx.post(
    'https://api.deepseek.com/chat/completions',
    json={
        'model': 'deepseek-chat',
        'messages': [
            {'role': 'system', 'content': '你是一名助手'},
            {'role': 'user', 'content': '你好'}
        ],
        'stream': False
    },
    headers={
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {API_KEY}'
    },
    timeout=60
)
print(resp.status_code)
print(resp.text)