import os

class Environments:
    def __init__(self):
        self.region = os.environ.get("AWS_REGION", "us-east-1")

