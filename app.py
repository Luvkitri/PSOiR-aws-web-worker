import time
import boto3

import threading
from threading import Thread

'''
Worker:​

- reads message from queue, ​
- loads corresponding file from S3, ​
- perfoms operation on the data ​
- saves result to S3​

deletes message from queue.
'''

REGION_NAME = 'us-east-1'

# Queue variables
QUEUE_NAME = 'psior-task-queue'
QUEUE_URL = 'https://sqs.us-east-1.amazonaws.com/852832888511/psior-task-queue'

# S3 variables
S3_BUCKET_NAME = 'psior-task'

exit_signal = threading.Event()

class WorkerThread(Thread):
  """Class representing worker task which takes care of:
  - loading coresponding file from s3
  - performing operations on file data
  - saving result to S3

  Args:
      Thread ([type]): [description]
  """
  
  def __init__(self):
    Thread.__init__(self)


class SQSFetchThread(Thread):
  """Class representing main worker thread which takes care of fetching messages from the sqs queue

  Args:
      Thread (Thread): [description]
  """
  def __init__(self):
    Thread.__init__(self)
    
    self.delay: float = 10.0

    # Get the service resource
    self.sqs = boto3.resource('sqs', region_name=REGION_NAME)

    # Get the queue
    self.queue = self.sqs.get_queue_by_name(QueueName=QUEUE_NAME)

  def run(self):
    while not exit_signal.is_set():
      # Process messages by printing out body and optional author name
      for message in self.queue.receive_messages():
        # Print out the body and author (if set)
        print(f'{message.body}')


def main():
  print('Starting worker...')
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