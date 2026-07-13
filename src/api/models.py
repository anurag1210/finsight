from pydantic import BaseModel, field_validator

class QueryRequest(BaseModel):
    query: str
    
    @field_validator('query')
    @classmethod
    def query_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Query cannot be empty')
        if len(v.strip()) < 3:
            raise ValueError('Query too short')
        if len(v) > 2000:
            raise ValueError('Query too long — maximum 2000 characters')
        return v.strip()

class QueryResponse(BaseModel):
    answer: str