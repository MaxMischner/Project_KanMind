from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError


def custom_exception_handler(exc, context):
    """
    Custom exception handler that converts validation errors about missing resources to 404.
    
    Note: 401/403 are now handled by TokenAuthentication and IsAuthenticatedWithProper401 classes.
    This handler only converts "does not exist" errors to 404 instead of 400.
    """

    response = exception_handler(exc, context)
    
    # Convert validation errors about missing resources to 404
    if isinstance(exc, ValidationError):
        if response is not None and response.status_code == 400:
            if isinstance(response.data, dict):
                for field, messages in response.data.items():
                    if isinstance(messages, list):
                        for msg in messages:
                            if 'does not exist' in str(msg) or 'Invalid pk' in str(msg):
                                response.status_code = 404
                                break
    
    return response
