class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: Union[str, None] = None
