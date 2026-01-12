from rest_framework.views import exception_handler
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed, ValidationError
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Custom exception handler that properly returns 401 for authentication failures
    and 404 for related object not found errors.
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    # If the exception is about authentication, ensure it returns 401
    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        if response is not None:
            response.status_code = 401
    
    # Check if it's a ValidationError about invalid pk (relationship not found)
    # This happens when board_id doesn't exist - should be 404, not 400
    if isinstance(exc, ValidationError):
        if response is not None and response.status_code == 400:
            # Check if the error is about invalid primary key
            if isinstance(response.data, dict):
                for field, messages in response.data.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            if 'does not exist' in str(msg) or 'Invalid pk' in str(msg):
                                response.status_code = 404
                                break
    
    return response
