from fastapi import Request


async def handle_ip_or_api_key(request: Request, api_key: str = None):
    print(request.client.host, api_key)
