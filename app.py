import json

from starlette.routing import Route
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse, JSONResponse

async def get_all(request, debug=True):
    await request.body()
    if debug:
        print(request._body)
    j = {}
    return JSONResponse(j)


async def request_handler(request, debug=True):
    '''
    # TODO
    :return: quotation in minutes or something
    '''
    await request.body()
    print(request._body)
    j = json.loads(request._body)
    if debug:
        print(f'\n j in request_handler: {j} \n')

    await m.act()

    return PlainTextResponse(msg)

app = Starlette(debug=True, routes=[
    Route('/q', request_handler, methods=['GET', 'POST']),
    Route('/get_all', get_all, methods=['GET']),

])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
