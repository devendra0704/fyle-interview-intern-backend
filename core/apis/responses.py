# from flask import Response, jsonify, make_response


# class APIResponse(Response):
#     @classmethod
#     def respond(cls, data):
#         return make_response(jsonify(data=data))


from flask import Response, jsonify, make_response

class APIResponse(Response):
    @classmethod
    def respond(cls, data, message=None, error=None, status_code=200):
        response_data = {
            "data": data,
            "message": message,
            "error": error
        }
        return make_response(jsonify(response_data), status_code)
