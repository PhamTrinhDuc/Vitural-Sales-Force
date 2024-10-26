from typing import Dict
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from source.model.loader import ModelLoader
from configs.config_fewshot import LoadConfig


llm = ModelLoader().load_rag_model()

def split_sentences(text_input: str, examples: Dict) -> str:

    """
    Sử dụng few shot để trích xuất thông tin như giá ,sản phẩm, công suất ... từ câu hỏi của người dùng.
    Args:
        text_input: câu hỏi của người dùng.
        examples: các ví dụ về thông tin của sản phẩm cần trích xuất.
    Return:
        Trả về thông tin trích xuất của sản phẩm từ câu hỏi của người dùng.
    """

    example_template = """
        Input command from user: {input_text}
        The information extracted from above command:\n
        ----
        object: {object}
        price: {price}
        power: {power}
        weight: {weight}
        volume: {volume}
        specifications: {specifications}
    """

    example_prompt = PromptTemplate(
        input_variables=["input_text", "object", "price", "power", "weight", "volume", "specifications"],
        template=example_template,
    )

    few_shot_prompt = FewShotPromptTemplate(
        # These are the examples we want to insert into the prompt.
        examples=examples,
        # This is how we want to format the examples when we insert them into the prompt.
        example_prompt=example_prompt,
        # The prefix is some text that goes before the examples in the prompt.
        prefix="Extract detailed information for an input command asking. Return the corresponding object. Below are some examples:",
        # The suffix is some text that goes after the examples in the prompt.
        # Usually, this is where the user input will go
        suffix="Input command from user: {input_text}\nThe information extracted from above command:",
        # The input variables are the variables that the overall prompt expects.
        input_variables=["input_text"],
        # The example_separator is the string we will use to join the prefix, examples, and suffix together with.
        example_separator="\n\n",
    )
    chain = few_shot_prompt | llm
    result = chain.invoke(input=text_input).content
    return result.lower()

def extract_info(sentences: str, examples: Dict) -> Dict:

    """
    Xử lý kết quả sau khi few shot của LLM để đưa về đúng định dạng mong muốn.
    Args:
        sentences: câu hỏi của người dùng.
        examples: các ví dụ về thông tin của sản phẩm cần trích xuất.
    Return:
        Trả về thông tin trích xuất của sản phẩm theo đúng format mong muốn.
    """

    try:
        sentece_splitted = split_sentences(sentences, examples)
        variables = {}
        lines = sentece_splitted.strip().split('\n')
        for line in lines:
            parts = line.split(':')
            if len(parts) == 2:
                key = parts[0].strip()
                price = parts[1].strip()
                if key == 'object':
                    # Xử lý phần object
                    # Loại bỏ các dấu ngoặc và khoảng trắng
                    price = price.replace('[', '').replace(']', '').strip()
                    # Tách các giá trị theo dấu phẩy
                    object_list = [item.strip().strip("'") for item in price.split(',') if item.strip()]
                    variables[key] = object_list
                else:
                    variables[key] = price       
        return variables
    except Exception as e:
        s = {'object': sentences, 'power':'', 'prices':[''], 'weight': '','volume':'','specifications':''}
        print('extract object in few shot: ', s['object'])
        return s
    
def classify_intent(question: str) -> Dict:
    """
    Phân loại câu hỏi của người dùng vào các loại: giá, công suất, dung tích, khối lượng, số lượng, thông tin chung.

    Args:
        question: câu hỏi của người dùng.
    """

    # Các specifications cần phân loại
    specifications = ["giá", "công suất", "dung tích", "khối lượng", "số lượng","thông tin chung"]
    # Tạo prompt để phân loại câu hỏi
    prompt_template = """
    Phân loại câu hỏi sau đây chỉ một trong các loại sau: {specifications}.

    Câu hỏi: {question}

    Loại:
    """
    prompt = PromptTemplate(
        input_variables=["specifications", "question"],
            template=prompt_template,
    )

    chain = prompt | llm

    # Hàm phân loại câu hỏi
    query_classified = chain.invoke({
        "specifications": ", ".join(specifications),
        "question": question
    }).content

    if "giá" in query_classified.lower():
        examples = LoadConfig.EXAMPLE_PRICE
        json_fewshoted =  extract_info(question, examples)
    elif "công suất" in query_classified.lower():
        examples = LoadConfig.EXAMPLE_POWER
        json_fewshoted =  extract_info(question, examples)
    elif "khối lượng" in query_classified.lower():
        examples = LoadConfig.EXAMPLE_WEIGHT
        json_fewshoted =  extract_info(question, examples)
    elif "dung tích" in query_classified.lower():
        examples = LoadConfig.EXAMPLE_VOLUME
        json_fewshoted =  extract_info(question, examples)
    else:
        examples = LoadConfig.EXAMPLE_QUANTITY
        json_fewshoted =  extract_info(question, examples)

    return json_fewshoted

    