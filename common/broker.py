# common/broker.py
import pika
from common.config import RABBITMQ_HOST, RABBITMQ_QUEUE

def publish_game_result(message):
    connection = None
    try:
        # Устанавливаем соединение с RabbitMQ, используя настройки из config.py
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        channel = connection.channel()

        # Объявляем очередь. Если очередь не существует, она будет создана.
        channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)

        # Публикуем сообщение в очередь
        channel.basic_publish(
            exchange='',
            routing_key=RABBITMQ_QUEUE,
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)  # Указывает, что сообщение постоянное
        )
        print(" [x] Sent %r" % message)
    except Exception as e:
        print(f"Ошибка при отправке сообщения в RabbitMQ: {e}")
    finally:
        if connection and connection.is_open:
            connection.close()
