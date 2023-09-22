import aiohttp.web
import aiohttp.web_ws
import aiohttp_jinja2
import jinja2

from aiohttp import web
from config.config_app import STATIC_PATH, STATIC_MAIN, START_HOST, SOCKET_ENDPOINT, START_PORT
from handlers.socket_handler import websocket_handler
from logs.logs import my_logger
from utils.utils3 import check_redis_connection, check_sistem


async def index(request):
    context = {'title': 'Пишем первое приложение на aiohttp',
               'socket_endpoint': SOCKET_ENDPOINT }
    return aiohttp_jinja2.render_template('index.html', request, context=context)


app = aiohttp.web.Application()
app['debug'] = True
loader = jinja2.FileSystemLoader('templates')
aiohttp_jinja2.setup(app, loader=loader)

app.router.add_get('/ws', websocket_handler)
app.router.add_get('/', index)
app.add_routes([web.static('/static', path=STATIC_PATH)])
app.add_routes([web.static('/static_main', path=STATIC_MAIN)])

for resource in app.router.resources():
    if isinstance(resource, web.StaticResource):
        print("Static files path:", resource.get_info())
        break

def main():
    my_logger.info('Старт приложения в режиме TEST MODE')
    check_redis_connection()
    check_sistem()
    aiohttp.web.run_app(app, host=START_HOST, port=START_PORT)




if __name__ == '__main__':
    main()
