from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed


def custom_exception_handler(exc, context):
    """
    Custom exception handler that properly returns 401 for authentication failures.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    # If the exception is about authentication, ensure it returns 401
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        if response is not None:
            response.status_code = 401
    
    return response
