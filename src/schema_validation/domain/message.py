from domain.api_model import ResponseObject, ErrorResponseObject

class ResponseMessage:

    @staticmethod
    def rep_200(message: str, type: str, category: str, id: str):
        return ResponseObject(
                statusCode=200,
                id=id,
                type=type,
                category=category,
                message=message
            )
    
    @staticmethod
    def rep_400(message: str, type: str, category: str, id: str):
        return ErrorResponseObject(
                statusCode=400,
                id=id,
                type=type,
                category=category,
                message=message
            )