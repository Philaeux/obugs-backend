import logging

import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s")

# Entrypoint
if __name__ == '__main__':
    from obugs.settings import Settings
    from obugs.backend import make_app

    settings = Settings()
    settings.load_from_ini()

    app = make_app(settings)
    uvicorn.run(app, host="0.0.0.0", port=5000)
