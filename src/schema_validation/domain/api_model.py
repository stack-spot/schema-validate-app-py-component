from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class ResponseObject:
    id: str 
    type: str
    statusCode: int
    category: str
    message: str

    @property
    def format_report(self):
        return {
            'statusCode': self.statusCode,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'requestId': self.id,
                'eventType': self.type,
                'eventCategory': self.category,
                'eventMessage': self.message,
                'eventTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        }

@dataclass
class ErrorResponseObject:
    id: str 
    type: str
    statusCode: int
    category: str
    message: str

    @property
    def format_report(self):
        return {
            'statusCode': self.statusCode,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'requestId': self.id,
                'errorType': self.type,
                'errorCategory': self.category,
                'errorMessage': self.message,
                'errorTime': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        }