import asyncio
import websockets
from aiohttp import web
from urllib.parse import parse_qs
import aiohttp
import db

connected = set()

#===================================================

async def hello(request):
    return web.FileResponse('/app/src/templates/home.html')

#===================================================

async def read_cookie_handler(request):
    cookie_value = request.headers.get('fuck_niggers')
    query_parameters = request.rel_url.query.getall('token')[0]
    full_url = str(request.url)
    print(cookie_value, query_parameters, full_url)

    if cookie_value:
        asd = await db.check_token(cookie_value)
        return asd, cookie_value
    else:
        print("query_parameters", query_parameters)
        if await db.check_token(query_parameters):
            return True, query_parameters
        else:
            return False, None
        
#===================================================

async def login(request):
    data = await request.post()
    username = data.get('username', '')
    password = data.get('password', '')
    if username and password:
        res, token = await db.login(username, password)
        print(res)
        if res:
            print("[+] TOKEN: ", token)
            return web.HTTPFound(f'https://0.0.0.0/chat_page?token={token}')
    else:
        return web.Response(text="no creds")


async def register(request):
    data = await request.post()
    username = data.get('username', '')
    password = data.get('password', '')
    if username and password:
        res, text = await db.register(username, password)
        if res:
            return web.HTTPFound(f'https://0.0.0.0/login_page')
        else:
            return web.HTTPFound(f'https://0.0.0.0/login_page')
    else:
        return web.Response(text="no creds")

#===================================================

async def avaliable_rooms(request):
        rooms = await db.rooms()
        return web.Response(text=f"{rooms}")

#===================================================

def is_authenticated(func):
    async def wrapper(request, *args, **kwargs):
        resp, token =  await read_cookie_handler(request)
        print(resp, token)
        if resp:
            return await func(request, token, *args, **kwargs)
        return web.Response(text=f"not authed")
    return wrapper

#===================================================

@is_authenticated
async def hello_auth(request, token):
    return web.Response(text="Hello, hello_auth!")

websockets = []

@is_authenticated
async def websocket_handler(request, token):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    websockets.append(ws)
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(websockets)
                for _ws in websockets:
                    await _ws.send_str(msg.data)
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print('ws connection closed with exception %s' % ws.exception())

    finally:
        websockets.remove(ws)

    return ws

#===================================================

async def login_page(request):
    return web.FileResponse('/app/src/templates/login.html')

async def register_page(request):
    return web.FileResponse('/app/src/templates/register.html')

async def chat_page(request):
    return web.FileResponse('/app/src/templates/chat.html')

async def chat_css(request):
    return web.FileResponse('/app/src/static/css/chat.css')

async def login_register(request):
    return web.FileResponse('/app/src/static/css/login_register.css')

async def home(request):
    return web.FileResponse('/app/src/static/css/home.css')

async def image(request):
    return web.FileResponse('/app/src/static/img/logo-white.png')

#===================================================

app = web.Application()

#===================================================

app.router.add_get('/', hello)
app.router.add_post('/login', login)
app.router.add_post('/register', register)
app.router.add_get('/hello_auth', hello_auth)
app.router.add_get('/rooms', avaliable_rooms)
app.router.add_get('/chat', websocket_handler)
app.router.add_get('/login_page', login_page)
app.router.add_get('/register_page', register_page)
app.router.add_get('/chat_page', chat_page)
app.router.add_get('/app/src/static/css/chat.css', chat_css)
app.router.add_get('/app/src/static/css/login_register.css', login_register)
app.router.add_get('/app/src/static/css/home.css', home)
app.router.add_get('/app/src/static/img/logo-white.png', image)

#===================================================

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=6001)
