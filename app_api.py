import uvicorn
from typing import Union
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File
from api.handle_request import handle_request

app = FastAPI()
numberrequest = 0

@app.post('/chatbot_proactive')
async def post(
    idRequest: str = Form(...),
    nameBot: str = Form(...),
    phoneNumber: str = Form(...),
    userName: str = Form(...),
    inputText: str = Form(None),
    address: str = Form(None),
    image: Union[UploadFile, str, None] = File(default=None),
    voice: Union[UploadFile, str, None] = File(default=None)
):
    global numberrequest
    numberrequest += 1

    print("----------------NEW_SESSION--------------")
    print("NumberRequest", numberrequest)
    print("User  = ", userName)
    print("InputText  = ", inputText)

    image = None if isinstance(image, str) and image == "" else image
    voice = None if isinstance(voice, str) and voice == "" else voice

    results = handle_request(
        InputText=inputText,
        IdRequest=idRequest,
        NameBot=nameBot,
        UserName=userName,
        Image=image,
        Voice=voice,
        PhoneNumber=phoneNumber,
        Address=address
    )

    print("----------------HANDLE_REQUEST_OUTPUT--------------")
    print(results)

    return results

uvicorn.run(app, host="0.0.0.0", port=8000)