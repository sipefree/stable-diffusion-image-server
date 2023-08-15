from sanic import Sanic
from sanic.response import text
from .cli_args import AppConfig


app = Sanic('StableDiffusionImageServer', env_prefix='SDIS_')


@app.before_server_start
def init_db_connection(app: Sanic):
    pass

if __name__ == '__main__':
    config = AppConfig()
    app.update_config(config)
    app.run(host=config.LISTEN_ADDR,
            port=config.PORT,
            debug=config.DEBUG)