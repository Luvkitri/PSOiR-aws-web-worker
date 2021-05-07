import time

import boto3
from botocore.exceptions import ClientError
from os import path, remove

import threading
from threading import Thread


"""
Worker:​

- reads message from queue, ​
- loads corresponding file from S3, ​
- perfoms operation on the data ​
- saves result to S3​

deletes message from queue.
"""

REGION_NAME = "us-east-1"

# Queue variables
QUEUE_NAME = "psior-task-queue"
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/852832888511/psior-task-queue"

# S3 variables
S3_BUCKET_NAME = "psior-task"

exit_signal = threading.Event()


class WorkerThread(Thread):
    """Class representing worker task which takes care of:
    - loading coresponding file from s3
    - performing operations on file data
    - saving result to S3

    Args:
        Thread ([type]): [description]
    """

    def __init__(self, file_name, message):
        Thread.__init__(self)

        self.s3 = boto3.client("s3")

        self.file_name = file_name
        self.message = message

    def editContent(self, file_content):
        words = file_content.split(" ")
        new_content = ""

        print(words)

        for word in words:
            if word == "":
                continue

            if len(word) > 1:
                edited_word = word[0].upper() + word[1:]
            else:
                edited_word = word[0].upper()

            new_content += edited_word + " "

        return (
            "This file was edited using worker\n Each word in text starts with uppercase letter\n"
            + new_content
        )

    def run(self):
        print(f"Worker on {threading.current_thread().name} has started...")

        # Create a path for downloaded file
        temp_file_path = path.abspath("tmp/" + path.basename(self.file_name))

        # Download a file
        with open(temp_file_path, "wb") as f:
            self.s3.download_fileobj(S3_BUCKET_NAME, self.file_name, f)

        # Open and read downloaded file
        file_content = ""
        with open(temp_file_path, "r") as f:
            file_content = f.read()

        # Do work on a downloaded file
        new_content = self.editContent(file_content)

        # Save edited file
        with open(temp_file_path, "w") as f:
            f.write(new_content)

        # Upload the file
        edited_file_path = "edited/" + path.basename(self.file_name)

        try:
            response = self.s3.upload_file(temp_file_path, S3_BUCKET_NAME, edited_file_path)
        except ClientError as e:
            print(e)

        remove(temp_file_path)

        print(f"Worker on {threading.current_thread().name} has finished...")
        self.message.delete()


class SQSFetchThread(Thread):
    """Class representing main worker thread which takes care of fetching messages from the sqs queue

    Args:
        Thread (Thread): [description]
    """

    def __init__(self):
        Thread.__init__(self)

        self.delay: float = 10.0

        # Get the service resource
        self.sqs = boto3.resource("sqs", region_name=REGION_NAME)

        # Get the queue
        self.queue = self.sqs.get_queue_by_name(QueueName=QUEUE_NAME)

    def run(self):
        while not exit_signal.is_set():
            # Process messages by printing out body and optional author name
            for message in self.queue.receive_messages():
                # Print out the body and author (if set)
                print(f"{message.body}")
                worker = WorkerThread(message.body, message)
                worker.start()


def main():
    fetching_thread = SQSFetchThread()
    fetching_thread.start()

    try:
        # enable children threads to exit the main thread, too
        while not exit_signal.is_set():
            time.sleep(0.1)
    except KeyboardInterrupt:
        exit_signal.set()


if __name__ == "__main__":
    main()
