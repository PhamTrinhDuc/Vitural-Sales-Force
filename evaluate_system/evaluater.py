from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
    context_utilization
)
from source.router.router import decision_search_type
from source.generate.streamlit_chat import chat_interface
from source.retriever.chroma.retriever import get_context
from source.retriever.elastic import search_db
from configs.config_system import SYSTEM_CONFIG


class Evaluater:
    def __inti__(self):
        self.questions =[
            "Tôi muốn tìm điều hòa giá 10tr có tính năng inverter, diện tích làm mát khoảng 20m2", 
            "Nhà anh có diện tích phòng khoảng 50m2 thì có điều hòa nào phù hợp không?",
            "Anh cần tìm điều hòa có giá trên 10 triệu, công suất khoản 12000BTU trở lên",
            "Có điều hào nào phù hợp cho người già dùng không?",
            "Anh cần tìm điều hòa có diện tích làm mát lớn mà giá cả lại phải chăng",
            "So sánh cho anh điều hào 2 chiều và điều hòa 1 chiều",
            "Tôi muốn biết top 10 điều hào bán chạy trong năm 2024",
            "Em có chương trình khuyễn mãi nào cho điều hòa không?",
            "Có chính sách bảo hành nào cho điều hòa không?",
            "Cho anh xem điều hào nào có công suất lớn nhất",
            "có bao nhiêu cái điều hòa có công suất trên 9000BTU, giá dưới 10 triệu, cân nặng trên 10kg không em",
            "Anh cần xem thông số chi tiết của điều hòa trên",
            "Có sản phẩm nào giống sản phẩm trên không em nhỉ?",
            "Em có bán điều hào nào có tính năng đuổi muỗi không?",
            "Anh cần em giải thích GAS R32 là gì?",
            ]
        self.answers = []
        self.contexts = []
        self.dataset = self.get_ground_truth()
    
    def get_ground_truth(self):
        """
        Lấy ra các thông tin câu hỏi, câu trả lời và phần context liên quan.
        Return:
            trả về dataset chứa thông tin câu hỏi, câu trả lời và context
        """
        for query in self.questions:
            response = chat_interface(query=query)
            self.answers.append(response)

            type = decision_search_type(query)
            if type == "ELS":
                context = search_db(query)
            else:
                context = get_context(query=query, db_name="dieu_hoa")
            self.contexts.append(context)
        data = {
            "question": self.questions,
            "answer": self.answers,
            "context": self.contexts
        }               

        return Dataset.from_dict(data)

    def evaluate(self):
        """
        Sử dụng các metric để đánh giá hệ thống thông qua dataset vừa tạo.
        """
        result = evaluate(
            dataset=self.dataset,
            metrics=[
                context_utilization,
                faithfulness,
                answer_relevancy
            ],
            llm=SYSTEM_CONFIG.load_rag_model(),
            embeddings=SYSTEM_CONFIG.load_embed_openai_model(),
        ) 

        result_df = result.to_pandas()
        result_df.to_csv("data/evaluate_result.csv")
        return result_df


