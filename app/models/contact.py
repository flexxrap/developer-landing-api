import re

from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactRequest(BaseModel):
    name: str = Field(..., examples=["Иван Иванов"])
    phone: str = Field(..., examples=["+79991234567"])
    email: EmailStr = Field(..., examples=["ivan@example.com"])
    comment: str = Field(..., examples=["Хочу обсудить проект"])

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 2:
            raise ValueError("Имя должно содержать минимум 2 символа")
        if len(stripped) > 50:
            raise ValueError("Имя должно содержать не более 50 символов")
        return stripped

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)]", "", v)
        if not re.match(r"^\+?[1-9]\d{6,14}$", cleaned):
            raise ValueError("Неверный формат телефона. Пример: +79991234567")
        return cleaned

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Комментарий должен содержать минимум 10 символов")
        if len(stripped) > 500:
            raise ValueError("Комментарий должен содержать не более 500 символов")
        return stripped


class ContactResponse(BaseModel):
    success: bool
    message: str
