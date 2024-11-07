import os
import dotenv
from openai import OpenAI
from utils.utils_retriever import RetrieveHelper 
from configs.config_system import LoadConfig

dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")


tools = [
        {
            "type": "function",
            "function": {
                "name": "get_specifications",
                "description": """Lấy ra loại hoặc tên sản phẩm và các thông số kỹ thuật của sản phẩm có trong câu hỏi. Sử dụng khi câu hỏi có thông tin về 1 trong các các thông số [loại hoặc tên sản phẩm,  giá, cân nặng, công suất hoặc dung tích]""",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "group": {
                            "type": "string",
                            "description": f"""lấy ra nhóm sản phẩm có trong câu hỏi từ list: {LoadConfig.LIST_GROUP_NAME}. 
                            Chỉ trả ra tên group có trong list đã cho trước"""
                        },
                        "object": {
                            "type": "string",
                            "description": "tên hoặc loại sản phẩm có trong câu hỏi. Ví dụ: điều hòa, điều hòa MDV 9000BTU, máy giặt LG ...",
                        },
                        "price": {
                            "type": "string",
                            "description": "giá của sản phẩm có trong câu hỏi. Ví dụ : 1 triệu, 1000đ, ...",
                        },
                        "power": {
                            "type": "string", 
                            "description": "công suất của sản phẩm có trong câu hỏi. Ví dụ : 5W, 9000BTU, ..."
                        },
                        "weight": {
                            "type": "string", 
                            "description": "cân nặng của sản phẩm có trong câu hỏi. Ví dụ : 1 cân, 10kg, 20 gam, ..."
                        },
                        "volume": {
                            "type": "string", 
                            "description": "dung tích của sản phẩm có trong câu hỏi. Ví dụ : 1 lít, 3 mét khối ..."
                        },
                        "intent": {
                            "type": "string",
                            "description": "ý định của người dùng khi hỏi câu hỏi. Ví dụ: mua, tìm hiểu, so sánh, ..."
                        }
                    },
                    "required": ["group", "object", "price", "power", "weight", "volume", "intent"],
                },
            },
        }
    ]

def extract_info(query: str):
    client = OpenAI(timeout=LoadConfig.TIMEOUT)

    messages = [
        {'role': 'system', 'content': '''Bạn là 1 chuyên gia extract thông tin từ câu hỏi. 
        Hãy giúp tôi lấy các thông số kỹ thuật, tên hoặc loại của sản phẩm có trong câu hỏi
        Lưu ý:
            + nếu câu hỏi hỏi về các thông số lớn, nhỏ, rẻ, đắt... thì trả ra cụm đó. 
            + Nếu không có thông số nào thì trả ra '' cho thông số ấy.
            + 1 số tên sản phẩm có chứa cả thông số thì bạn cần tách thông số đó sang trường của thông số đó'''},
        {"role": "user", "content": query}]

    openai_response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
    
     # if openai_response.choices[0].message.tool_calls:
    #     for i in range(0, len(openai_response.choices[0].message.tool_calls)):
    #         print(f"Function: {openai_response.choices[0].message.tool_calls[i].function.name}\n")
    #         print(f"Arguments: {openai_response.choices[0].message.tool_calls[i].function.arguments}\n")
    arguments = openai_response.choices[0].message.tool_calls[0].function.arguments
    
    specifications = RetrieveHelper().parse_string_to_dict(arguments)
    return specifications


def main():
    arguments = extract_info("Tôi muốn mua điều hòa rẻ nhất")
    json_arguments = RetrieveHelper().parse_string_to_dict(arguments)
    print(json_arguments)
    for key, value in json_arguments.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()