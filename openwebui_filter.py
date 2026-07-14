"""
title: LLMLingua-2 Advanced Tool-Aware Compressor
author: syuza
version: 1.0.0
description: MCPツールやRAGの直後の長文を確実に検知し、mlx-comp APIを使って安全に自動圧縮する完全版フィルター。
"""

import aiohttp
from pydantic import BaseModel, Field
from typing import List, Dict, Any


class Filter:
    class Valves(BaseModel):
        compression_rate: float = Field(default=0.5, description="圧縮率 (0.1〜0.9)")
        api_url: str = Field(default="http://host.docker.internal:8081/compress", description="mlx-compのAPIエンドポイント。Docker環境からは host.docker.internal を推奨")
        timeout: int = Field(default=30, description="APIタイムアウト秒数")

    def __init__(self):
        self.type = "inlet"
        self.valves = self.Valves()

    async def emit_status(
        self,
        __event_emitter__,
        description: str,
        status: str = "in_progress",
        done: bool = False,
    ):
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {
                        "description": description,
                        "status": status,
                        "done": done,
                    },
                }
            )

    async def inlet(self, body: Dict, __event_emitter__: Any = None) -> Dict:
        messages = body.get("messages", [])

        # MCPツール応答や150文字以上の長文を検知
        target_indices = []
        text_to_compress_parts = []
        for i, m in enumerate(messages):
            if m.get("role") != "system" and (
                m.get("role") == "tool" or len(m.get("content", "")) >= 150
            ):
                target_indices.append(i)
                text_to_compress_parts.append(m.get("content", ""))

        if not target_indices:
            return body

        first_target_idx = target_indices[0]

        # 圧縮API呼び出し
        try:
            await self.emit_status(__event_emitter__, "LLMLingua-2でコンテキストを圧縮中...", "in_progress")
            
            combined_text = "\n\n".join(text_to_compress_parts)
            timeout = aiohttp.ClientTimeout(total=self.valves.timeout)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.valves.api_url,
                    json={
                        "text": combined_text,
                        "rate": self.valves.compression_rate,  # FastAPI側の引数「rate」にマッピング
                    },
                ) as response:
                    if response.status == 200:
                        res_data = await response.json()
                        compressed_text = res_data.get("compressed_text", "")
                        await self.emit_status(__event_emitter__, "コンテキストの圧縮が完了しました", "complete", done=True)
                    else:
                        raise Exception(f"API Error: {response.status}")

            # メッセージ再構成
            final_messages = []
            for i, m in enumerate(messages):
                if i == first_target_idx:
                    new_m = m.copy()
                    new_m["content"] = f"{compressed_text}\n\n(Optimized via mlx-comp)"
                    final_messages.append(new_m)
                elif i in target_indices:
                    new_m = m.copy()
                    new_m["content"] = "[Compressed]"
                    final_messages.append(new_m)
                else:
                    final_messages.append(m)

            body["messages"] = final_messages
        except Exception as e:
            # サーバーが落ちている場合などは圧縮をスキップしてそのまま通す（安全弁）
            await self.emit_status(__event_emitter__, f"圧縮スキップ（サーバー未起動またはエラー）: {str(e)}", "complete", done=True)
            pass

        return body

