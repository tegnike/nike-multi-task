from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from services.tts import text_to_wav_by_google, text_to_wav_by_elevenlabs, text_to_wav_by_voicevox
from datetime import datetime
from dotenv import load_dotenv
import os
import re
import json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

output_dir = "./output"

@app.post("/upload/")
async def upload_text_file(file: UploadFile = File(...), type: str = Form(None)):
    if file.filename.endswith('.txt'):
        contents = await file.read()
        print("type:", type)
        if type == 'google':
            wav_audio = text_to_wav_by_google(contents.decode('utf-8'))
        elif type == 'elevenlabs':
            wav_audio = text_to_wav_by_elevenlabs(contents.decode('utf-8'))
        elif type == 'voicevox':
            wav_audio = text_to_wav_by_voicevox(contents.decode('utf-8'))
        else:
            raise HTTPException(status_code=400, detail="Invalid type. Please specify type.")

        # ファイル名から.txt拡張子を除去
        filename_without_extension = file.filename.rsplit('.', 1)[0]
        # 出力ファイル名を生成
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{type}_{filename_without_extension}.wav"
        output_path = f"{output_dir}/{filename}"
        with open(output_path, 'wb') as out:
            out.write(wav_audio)

        # 生成されたファイル名をレスポンスとして返す
        print(output_path)
        return {"message": "Audio content written", "filename": filename}
    else:
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload .txt file.")

@app.post("/json_sort")
async def sort_json(file: UploadFile = File(...)):
    contents = await file.read()
    # JSONファイルを読み込む
    data = json.loads(contents.decode('utf-8'))
    print(data)
    # 文字列の文字数が多い順にソートし、その後a-z順にソート
    sorted_data = dict(sorted(data.items(), key=lambda x: (-len(x[0]), x[0])))
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_en_to_ja.json"
    output_path = f"{output_dir}/{filename}"

    # ソートされたJSONを同じファイルに保存
    with open(output_path, 'w', encoding="utf-8") as f:
        json.dump(sorted_data, f, ensure_ascii=False, indent=2)

    return {"message": "Audio content written", "filename": filename}

@app.post("/process-json/")
async def process_json(file: UploadFile = None):
    # ファイルがアップロードされているか確認
    if not file:
        raise HTTPException(status_code=400, detail="File is required.")
    
    # UploadFileからデータを直接読み取る
    file_content = await file.read()
    data = json.loads(file_content)

    # 英単語を抽出
    words = []
    for item in data:
        if 'message' in item:
            words.extend(re.findall(r'\b[a-zA-Z]+\b', item['message']))

    # 抽出した英単語をキーとして、valueをすべてnullにしたJSONを作成
    output_data = {word: None for word in words}

    # JSONファイルに書き出す
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_processed.json"
    output_path = f"{output_dir}/{filename}"
    with open(output_path, 'w') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    return JSONResponse(content={"filename": filename})

@app.get("/download/")
def download_wav_file(filename: str):
    file_path = f"{output_dir}/{filename}"
    return FileResponse(file_path, headers={"Content-Disposition": f"attachment; filename={filename}"})
