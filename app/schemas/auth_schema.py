from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)


class UserRegister(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(
        min_length=3,
        max_length=50,
        description="Nombre del usuario",
    )

    email: EmailStr

    password: SecretStr = Field(
        min_length=8,
        max_length=72,
        description=(
            "Minimo 8 caracteres, con mayuscula, minuscula "
            "y numero; sin espacios y maximo 72 bytes."
        ),
    )

    role: Literal["user"] = "user"

    @field_validator("name", mode="before")
    @classmethod
    def limpiar_nombre(cls, value):
        if isinstance(value, str):
            return value.strip()

        return value

    @field_validator("password")
    @classmethod
    def validar_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()

        if len(password.encode("utf-8")) > 72:
            raise ValueError(
                "La contraseña no puede superar 72 bytes."
            )

        if any(character.isspace() for character in password):
            raise ValueError(
                "La contraseña no puede contener espacios."
            )

        if "\x00" in password:
            raise ValueError(
                "La contraseña contiene un caracter no permitido."
            )

        if not any(character.isupper() for character in password):
            raise ValueError(
                "La contraseña debe incluir una mayuscula."
            )

        if not any(character.islower() for character in password):
            raise ValueError(
                "La contraseña debe incluir una minuscula."
            )

        if not any(character.isdigit() for character in password):
            raise ValueError(
                "La contraseña debe incluir un numero."
            )

        return value


class Token(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"


class TokenData(BaseModel):
    user_id: int = Field(gt=0)