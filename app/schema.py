from pydantic import BaseModel

class JawabanInput(BaseModel):
    nama: str
    perguruan_tinggi: str
    id_pertanyaan: int
    jawaban: str

class SkorResponse(BaseModel):
    message: str
    total_score: int | None
    category: str | None





#
class UserInput(BaseModel):
    nama: str
    perguruan_tinggi: str

class AnswerInput(BaseModel):
    id_user: int
    id_pertanyaan: int
    jawaban: str

class BulkAnswerInput(BaseModel):
    id_user: int
    jawaban: list[str]  # harus 9 jawaban berurutan

