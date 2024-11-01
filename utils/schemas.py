from langchain_core.pydantic_v1 import BaseModel, Field

class GradeReWrite(BaseModel):
    """Viết lại câu hỏi của người dùng dựa trên câu hỏi và lịch sử."""
    rewrite: str = Field(description="Viết lại câu hỏi của người dùng dựa vào câu hỏi và lịch sử")

class SeachingDecision(BaseModel):
    """Lựa chọn giữa truy xuất bằng ELS hoặc TEXT, SIMILARITY|[tên sản phẩm] hoặc ORDER"""
    type: str = Field(description="Giá trị là TEXT hoặc ELS hoặc SIMILARITY|[tên sản phẩm], ORDER hoặc WEB")