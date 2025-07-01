from pydantic import BaseModel


class Test(BaseModel):
    id: int
    files: list[int]


print(getattr(Test(id=1, files=[1, 2, 3]), "files"))
