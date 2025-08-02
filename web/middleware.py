import traceback

class ExceptionHandleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwargs):
        return self.get_response(request)

    def process_exception(self, request, exception):
        print("--- Unhandled Exception ---")
        print(f"Path: {request.path}")
        print(f"User: {request.user}")
        print(f"Exception Type: {type(exception).__name__}")
        print(f"Exception Message: {exception}")
        print(f"Traceback: {traceback.format_exc()}")
        print("---------------------------")

        return None
