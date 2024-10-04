import uvicorn
from fastapi import FastAPI, Form
from fastapi import FastAPI, UploadFile, Form, File
from api.handle_request import handle_request

app = FastAPI()

@app.post('/chatbot')
async def post(
    InputText: str = Form(None),
    IdRequest: str = Form(...),
    NameBot: str = Form(...),
    UserName: str = Form(...),
    Voice: UploadFile = File(None),
    Image: UploadFile = File(None)
):
    
    results = handle_request(
        InputText=InputText,
        IdRequest=IdRequest,
        NameBot=NameBot,
        UserName=UserName,
    )
    print("Results from handle_request: ", results)

    return results
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8089)