import os
import json
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


load_dotenv()
api_key = os.getenv("AVALAI_API_KEY")

class FAQChatbot:
    """
    هسته اصلی چت‌بات مبتنی بر معماری RAG (Retrieval-Augmented Generation)
    این کلاس وظیفه تبدیل داده‌ها به بردار (Embedding)، ذخیره در ChromaDB و فراخوانی LLM را بر عهده دارد.
    """
    def __init__(self):
        
        if not api_key:
            raise ValueError("کلید AVALAI_API_KEY در فایل .env یافت نشد! لطفاً فایل .env را بررسی کنید.")

        
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key,
            base_url="https://api.avalai.ir/v1"
        )
        
        
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=api_key,
            base_url="https://api.avalai.ir/v1",
            temperature=0.5  
        )
        
        self.vector_store = None
        self.rag_chain = None
        
        
        self._setup_rag()

    def _format_docs(self, docs):
        """متد کمکی برای چسباندن اسناد بازیابی‌شده"""
        return "\n\n".join(doc.page_content for doc in docs)

    def _setup_rag(self):
        """بارگذاری داده‌ها، ساخت پایگاه داده برداری و زنجیره RAG"""
        
        
        data_path = os.path.join("data", "faq.json")
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"فایل داده در مسیر {data_path} یافت نشد!")

        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        
        documents = []
        for item in data:
            text = f"سوال: {item['question']}\nپاسخ: {item['answer']}"
            documents.append(Document(page_content=text))

        
        self.vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings
        )
        
        
        retriever = self.vector_store.as_retriever(search_kwargs={"k": 2})

        
        system_prompt = (
            "تو یک دستیار هوشمند فوق‌العاده، همه‌چیزدان و برنامه‌نویس حرفه‌ای هستی.\n\n"
            "مستندات آیین‌نامه دانشگاه (فقط در صورت مرتبط بودن استفاده کن):\n"
            "{context}\n\n"
            "قوانین پاسخگویی:\n"
            "۱. اگر سوال کاربر درباره قوانین، آیین‌نامه‌ها، مشروطی، حذف درس، سنوات یا امور دانشگاه بود، حتماً از مستندات بالا پاسخ دقیق بده.\n"
            "۲. اگر سوال کاربر مربوط به برنامه‌نویسی، نوشتن کد، مسائل علمی، اطلاعات عمومی یا گپ روزمره بود، آیین‌نامه را نادیده بگیر و با دانش عمومی خودت پاسخ جامع همراه با کد ارائه بده.\n"
            "۳. همیشه به زبان فارسی روان، محترمانه و کاربردی پاسخ بده.\n\n"
            "سوال کاربر: {question}"
        )

        prompt = ChatPromptTemplate.from_template(system_prompt)

        
        self.rag_chain = (
            {"context": retriever | self._format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def ask(self, query: str) -> str:
        """متد اصلی برای دریافت سوال کاربر و بازگرداندن پاسخ نهایی"""
        return self.rag_chain.invoke(query)