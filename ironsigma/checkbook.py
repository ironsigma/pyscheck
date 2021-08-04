import pathlib
import mariadb

from sanic import Sanic, response
from sanic.log import logger
from sanic.request import Request
from sanic.response import HTTPResponse

from ironsigma import env


app = Sanic("Checkbook")


# paths
pkg_path = pathlib.Path(__file__).parent
static_path = pkg_path.joinpath("static")

app.config.update(env.load(".env", "SANIC_"))


@app.main_process_start
async def open_db(app, loop):
    logger.info('DB pool created')


@app.before_server_start
async def db_connect(app, loop):
    app.ctx.db = mariadb.connect(
        host=app.config.DB_HOST, port=app.config.DB_PORT,
        user=app.config.DB_USER, password=app.config.DB_PASS,
        database=app.config.DB_NAME)
    logger.info('DB connection created')


@app.after_server_stop
async def db_close(app, loop):
    app.ctx.db.close()
    logger.info('DB connection closed')


@app.main_process_stop
async def close_db(app, loop):
    logger.info('DB pool release')


@app.get("/")
async def index(req: Request) -> HTTPResponse:
    logger.info("index called")

    cur = app.ctx.db.cursor()
    cur.execute("SELECT * FROM recurring")

    res = {"statuc": "OK", "rows": []}
    for row in cur:
        res["rows"].append(row)

    return response.json(res)


# Static paths
app.static("/static", static_path, name='static')
app.static("/favicon.ico", static_path.joinpath("favicon.ico"))
