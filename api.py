from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from rag_engine import FAQChatbot


app = FastAPI(
    title="🎓 سامانه هوشمند پاسخگویی دانشگاه API",
    description="رابط برنامه‌نویسی REST برای ارائه خدمات هوش مصنوعی و پاسخگویی به سوالات بر پایه معماری RAG",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


try:
    chatbot = FAQChatbot()
except Exception as e:
    print(f"❌ خطا در بارگذاری هسته RAG: {e}")
    chatbot = None


class QuestionRequest(BaseModel):
    question: str = Field(
        ..., 
        description="سوال کاربر درباره قوانین دانشگاه یا موضوعات دیگر",
        json_schema_extra={"example": "شرایط مشروطی در دانشگاه چیست؟"}
    )


class AnswerResponse(BaseModel):
    question: str = Field(..., description="سوال مطرح‌شده توسط کاربر")
    answer: str = Field(..., description="پاسخ تولیدشده توسط هوش مصنوعی و RAG")



@app.get("/", status_code=status.HTTP_200_OK)
def home():
    """نقطه پایانی بررسی سلامت وب‌سرویس (Health Check)"""
    return {
        "status": "Active",
        "message": "API چت‌بات هوشمند دانشگاه فعال است.",
        "documentation": "/docs"
    }

@app.post("/ask", response_model=AnswerResponse, status_code=status.HTTP_200_OK)
def ask_question(request: QuestionRequest):
    """نقطه پایانی اصلی برای دریافت سوال و بازگرداندن پاسخ هوشمند"""
    if not chatbot:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="سرویس هوش مصنوعی در دسترس نیست."
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="سوال نمی‌تواند خالی باشد."
        )
    
    try:
        
        response_text = chatbot.ask(request.question)
        
        return AnswerResponse(
            question=request.question,
            answer=response_text
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"خطایی در پردازش سوال رخ داد: {str(e)}"
        )