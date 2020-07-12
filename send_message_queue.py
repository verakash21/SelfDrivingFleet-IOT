import logging
import boto3
from botocore.exceptions import ClientError


def send_sqs_message(sqs_queue_url, msg_body):
    
    # Send the SQS message
    sqs_client = boto3.client('sqs')
    try:
        msg = sqs_client.send_message(QueueUrl=sqs_queue_url,
                                      MessageBody=msg_body)
    except ClientError as e:
        logging.error(e)
        return None
    return msg


def main():
    """Exercise send_sqs_message()"""

    # Assign this value before running the program
    sqs_queue_url = 'https://eu-west-1.queue.amazonaws.com/421962278521/Queue1'

    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)s: %(asctime)s: %(message)s')

    # Send some SQS messages
    
    msg_body = "SOS - Low battery level. Please change or recharge car battery."
    msg = send_sqs_message(sqs_queue_url, msg_body)
    if msg is not None:
        logging.info("Sent SQS message ID: " + str(msg["MessageId"]))


if __name__ == '__main__':
    main()
