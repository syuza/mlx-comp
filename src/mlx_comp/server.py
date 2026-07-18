import uvicorn
import gc
import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from llmlingua import PromptCompressor

# --- 1. FastAPI (LLMLingua-2 サーバー部) ---
app = FastAPI()

print("LLMLingua-2 モデルを読み込んでいます（Apple Silicon GPU最適化）...")
try:
    # 👈 正しい引数 `use_llmlingua2=True` を指定してLLMLingua-2モードで起動します
    compressor = PromptCompressor(
        model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
        use_llmlingua2=True,       # ⭐ これが公式の正しいLLMLingua-2切り替えスイッチです
        device_map="mps"           # MacのMシリーズGPUを使用
    )
    print("モデルの読み込みが完了しました。")
except Exception as e:
    print(f"GPUでの初期化に失敗しました。CPUで起動を試みます: {e}")
    try:
        compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-bert-base-multilingual-cased-meetingbank",
            use_llmlingua2=True,   # 👈 CPUフォールバック時も同様に指定
            device_map="cpu"
        )
        print("CPUでの読み込みが完了しました。")
    except Exception as e_cpu:
        print(f"完全な起動失敗: {e_cpu}")

class CompressRequest(BaseModel):
    text: str
    rate: float = 0.5

@app.post("/compress")
async def compress(payload: CompressRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="テキストが空です")
    try:
        print(f"\n[受信] 圧縮リクエストを受け付けました。元の文字数: {len(payload.text)}")

        # LLMLingua-2による高速圧縮処理
        results = compressor.compress_prompt(payload.text, rate=payload.rate)
        compressed = results["compressed_prompt"]

        # メモリ解放処理
        gc.collect() 
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

        print(f"[成功] 圧縮完了! -> 圧縮後の文字数: {len(compressed)}")
        return {"compressed_text": compressed}
    except Exception as e:
        print(f"[エラー] {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_server(host: str, port: int):
    print(f"FastAPI サーバーを起動します: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="info")

