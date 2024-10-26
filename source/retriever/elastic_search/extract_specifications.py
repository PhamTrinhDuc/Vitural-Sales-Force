import os
import dotenv
from openai import OpenAI
from .elastic_helper import ElasticHelper 


dotenv.load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
# os.environ['LANGCHAIN_TRACING_V2'] = 'true'
# os.environ['LANGCHAIN_ENDPOINT'] = 'https://api.smith.langchain.com'
# os.environ['LANGCHAIN_API_KEY'] = os.getenv("LANGCHAIN_API_KEY")


tools = [
        {
            "type": "function",
            "function": {
                "name": "get_specifications",
                "description": """Lấy ra loại hoặc tên sản phẩm và các thông số kỹ thuật của sản phẩm có trong câu hỏi. Sử dụng khi câu hỏi có thông tin về 1 trong các các thông số [loại hoặc tên sản phẩm,  giá, cân nặng, công suất hoặc dung tích]""",
                "parameters": {
                    "type": "object",
                    "properties": {
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
                    },
                    "required": ["object", "price", "power", "weight", "volume"],
                },
            },
        }
    ]

def extract_info(query: str):
    client = OpenAI()

    messages = [
        {'role': 'system', 'content': '''Bạn là 1 chuyên gia extract thông tin từ câu hỏi. 
        Hãy giúp tôi lấy các thông số kỹ thuật, tên hoặc loại của sản phẩm có trong câu hỏi
        Lưu ý:
            + nếu câu hỏi hỏi về các thông số lớn, nhỏ, rẻ, đắt... thì trả ra cụm đó. 
            + Nếu không có thông số nào thì trả ra '' cho thông số ấy.
            + 1 số tên sản phẩm có chứa cả thông số thì bạn cần tách thông số đó sang trường của thông số đó.'''},
        {"role": "user", "content": query}]

    openai_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
    arguments = openai_response.choices[0].message.tool_calls[0].function.arguments

    specifications = ElasticHelper().parse_string_to_dict(arguments)
    return specifications
    # if openai_response.choices[0].message.tool_calls:
    #     for i in range(0, len(openai_response.choices[0].message.tool_calls)):
    #         print(f"Function: {openai_response.choices[0].message.tool_calls[i].function.name}\n")
    #         print(f"Arguments: {openai_response.choices[0].message.tool_calls[i].function.arguments}\n")


if __name__ == "__main__":
    pass 
    # arguments = extract_info("Tôi muốn mua điều hòa rẻ nhất")
    # json_arguments = ElasticHelper().parse_string_to_dict(arguments)
    # print(json_arguments)
    # for key, value in json_arguments.items():
    #     print(f"{key}: {value}")
