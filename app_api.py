import uvicorn
from fastapi import FastAPI, Form
from fastapi import FastAPI, File, UploadFile
from fastapi import FastAPI, UploadFile, Form, File
from api.handle_request import handle_request, handle_title_conversation, handle_conversation

from configs import SYSTEM_CONFIG
app = FastAPI()
numberrequest = 0

@app.post('/chatbot_proactive')
async def post_request(
    idRequest: str = Form(...),
    nameBot: str = Form(...),
    phoneNumber: str = Form(...),
    userName: str = Form(...),
    inputText: str = Form(None),
    address: str = Form(None),
    image: UploadFile = File(None),
    voice: UploadFile = File(None)
    
):
    global numberrequest
    numberrequest += 1

    print("----------------NEW_SESSION--------------")
    print("NumberRequest = ", numberrequest)
    print("User = ", userName)
    print("PhoneNumber = ", phoneNumber)
    print("InputText = ", inputText)

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


@app.post('/get_conv_title')
async def get_title(phoneNumber: str = Form(...)): #10
    results = handle_title_conversation(phone_number=phoneNumber)
    return results

@app.post('/get_chat_conv')
async def post_session(
    phoneNumber: str = Form(...),
    sessionId: str = Form(...)
):  
    results =  handle_conversation(phone_number=phoneNumber, session_id=sessionId),
    return results

uvicorn.run(app, host="0.0.0.0", port=SYSTEM_CONFIG.PORT)
# uvicorn.run(app, host="0.0.0.0", port=8088)