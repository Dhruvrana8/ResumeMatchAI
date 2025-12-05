from fastapi import HTTPException


class UserError(HTTPException):
    """Base exception for user-related errors"""
    pass


class ChatError(HTTPException):
    """Base exception for chat-related errors"""
    pass


class UserNotFoundError(UserError):
    def __init__(self, user_id=None):
        message = "User not found" if user_id is None else f"User with id {user_id} not found"
        super().__init__(status_code=404, detail=message)

class UserAlreadyExistError(UserError):
    def __init__(self):
        message = "User already exists"
        super().__init__(status_code=404, detail=message)


class InvalidPasswordError(UserError):
    def __init__(self):
        super().__init__(status_code=401, detail="Current password is incorrect")


class PasswordMismatchError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="New passwords do not match")


class AuthenticationError(HTTPException):
    def __init__(self, message: str = "Could not validate user"):
        super().__init__(status_code=401, detail=message)


class ChatNotFoundError(ChatError):
    def __init__(self, chat_it=None):
        message = "Chat not found" if chat_it is None else f"Chat with id {chat_it} not found"
        super().__init__(status_code=404, detail=message)

class InvalidSenderError(ChatError):
    def __init__(self, chat_it=None):
        message = "The Sender can only be user or assistant"
        super().__init__(status_code=400, detail=message)

class PasswordValidationError(UserError):
    def __init__(self):
        super().__init__(status_code=400, detail="Password must contain at least one digit and one letter")