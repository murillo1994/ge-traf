import logging
import os
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("worker")

SYNC_INTERVAL = int(os.environ.get("SYNC_INTERVAL_SECONDS", 3600))


def run():
    os.environ.setdefault("FLASK_CONFIG", "production")
    from app import create_app
    from app.services.sync_metricas import sync_todas

    app = create_app(os.environ.get("FLASK_CONFIG", "production"))

    logger.info("Worker iniciado — sync a cada %d segundos", SYNC_INTERVAL)

    while True:
        with app.app_context():
            try:
                sync_todas()
            except Exception:
                logger.exception("Erro na sincronização")
        time.sleep(SYNC_INTERVAL)


if __name__ == "__main__":
    run()
