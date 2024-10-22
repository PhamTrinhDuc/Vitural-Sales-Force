from langchain_core.globals import set_llm_cache
from langchain_openai import ChatOpenAI
from langchain_core.caches import InMemoryCache
import time
import os
from dotenv import load_dotenv
from utils.timekeeper import timing_decorator
load_dotenv()
os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")


llm = ChatOpenAI(model="gpt-4o-mini-2024-07-18")
cache = InMemoryCache()
set_llm_cache(cache)
# The first time, it is not yet in cache, so it should take longer

@timing_decorator   
def test_cache_memory(prompt: str):
    start_time = time.time()
    result = llm.invoke(prompt).content
    end_time = time.time()
    return result, end_time - start_time

if __name__ == "__main__":
    # Original query
    original_prompt = "Tell me 2 jokes"
    result1, time1 = test_cache_memory(original_prompt)
    print(f"Original query:\nPrompt: {original_prompt}\nResult: {result1}\nTime: {time1:.2f} seconds\n")

    # Semantically similar query
    similar_prompt = "tell me 3 jokes"
    result2, time2 = test_cache_memory(similar_prompt)
    print(f"Similar query:\nPrompt: {similar_prompt}\nResult: {result2}\nTime: {time2:.2f} seconds\n")

    print(f"Speed improvement: {time1 / time2:.2f}x faster")
    # Clear the semantic cache
    # cache.clear()
    # print("Semantic cache cleared")