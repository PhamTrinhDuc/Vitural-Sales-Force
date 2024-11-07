import os
from dotenv import load_dotenv
import groq


load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")


client =groq.Groq()
completion = client.chat.completions.create(
    model="llama-3.2-90b-vision-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image?"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://upload.wikimedia.org/wikipedia/commons/f/f2/LPU-v1-die.jpg"
                    }
                }
            ]
        },
        {
            "role": "assistant",
            "content": ""
        }
    ],
    temperature=1,
    max_tokens=1024,
    top_p=1,
    stream=False,
    stop=None,
)

from PIL import Image
import io
import base64

image = Image.open("static/UI_1.png").convert("RGB")
image_bytes = io.BytesIO()
image.save(image_bytes, format='PNG')
image_bytes = image_bytes.getvalue()
base64_image = base64.b64encode(image_bytes).decode('ascii')


chat_completion = client.chat.completions.create(
        model="llama-3.2-90b-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Describe the image"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
print(chat_completion.choices[0].message)