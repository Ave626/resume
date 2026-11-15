from taskiq_aio_pika import AioPikaBroker
from app.core.infrastructure.config.settings import settings

broker = AioPikaBroker(settings.rabbitmq_url)
