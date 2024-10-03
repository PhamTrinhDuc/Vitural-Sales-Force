first_tools = [
        # Tool 1 - Get specifications
        { 
            "type": "function",
            "function": {
                "name": "get_specifications",
                "description": "Lấy ra các thông số kỹ thuật của sản phẩm có trong câu hỏi. Chỉ sử dụng khi câu hỏi yêu cầu thông tin cụ thể về giá, cân nặng, công suất hoặc dung tích.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "object": {
                            "type": "string",
                            "description": "tên sản phẩm có trong câu hỏi của người dùng.",
                        },
                        "price": {
                            "type": "string",
                            "description": "giá của sản phẩm có trong câu hỏi của người dùng. Ví dụ : 1 triệu, 1000đ, ...",
                        },
                        "power": {
                            "type": "string", 
                            "description": "công suất của sản phẩm có trong câu hỏi của người dùng. Ví dụ : 1W, 9000BTU, ..."
                        },
                        "weight": {
                            "type": "string", 
                            "description": "cân nặng của sản phẩm có trong câu hỏi. Ví dụ : 1 cân, 10kg, 20 gam, ..."
                        },
                        "volume": {
                            "type": "string", 
                            "description": "dung tích của sản phẩm có trong câu hỏi của người dùng. Ví dụ : 1 lít, 3 mét khối ..."
                        },
                    },
                    "required": ["object", "price", "power", "weight", "volume"],
                },
            },
        },
        # Tool 2 - Search similar products
        { 
            "type": "function",
            "function": {
                "name": "search_similar_products",
                "description": "Tìm kiếm sản phẩm tương tự. Chỉ sử dụng khi câu hỏi chứa các từ khóa như 'tương tự', 'giống', 'cùng loại', 'cùng hãng', 'cùng công suất', 'cùng dung tích', 'cùng cân nặng'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "object": {
                            "type": "string",
                            "description": "tên sản phẩm có trong câu hỏi của người dùng. Ví dụ: điều hòa MDV 10 triệu, điều hòa MDV-9000BTU",
                        }
                    },
                    "required": ["object"],
                },
            },
        },

        # Tool 3 - ORDER
        { 
            "type": "function",
            "function": {
                "name": "get_order",
                "description": "Xử lý yêu cầu đặt hàng. Chỉ sử dụng khi câu hỏi chứa các từ khóa liên quan đến việc mua hàng như 'đặt hàng', 'mua', 'giao hàng', 'đơn hàng', 'chốt đơn'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "object": {
                            "type": "string",
                            "description": "tên sản phảm có trong câu hỏi Ví dụ: . Nếu không có thì trả ra '' ",
                        }
                    },
                    "required": ["object"],
                },
            },
        },
    ]


from openai import OpenAI
import os
import dotenv
dotenv.load_dotenv()

os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
client = OpenAI()


question = "bên bạn có điều hòa MDV với công suất 9000 BTU  không ạ ?"
messages = [
    {"role": "system", "content": "Bạn hãy dựa vào câu hỏi và phần mô tả của hàm để lựa chọn hàm 1 cách chính xác nhất."},
    {"role": "user", "content": question}]


response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=first_tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
# Function for printing out responses neatly
def pprint_response(response):
    print("--- Full Response ---\n")
    print(response, "\n")
    
    print("--- Chat Completion Message ---\n")
    print(response.choices[0].message, "\n")
    
    if response.choices[0].message.tool_calls:
        for i in range(0, len(response.choices[0].message.tool_calls)):
            print(f"--- Tool Call {i+1} ---\n")
            print(f"Function: {response.choices[0].message.tool_calls[i].function.name}\n")
            print(f"Arguments: {response.choices[0].message.tool_calls[i].function.arguments}\n")

pprint_response(response)