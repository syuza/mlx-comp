# mlx-comp 🚀

`mlx-comp` は、Apple Silicon (MPS) の GPU パワーを最大限に活かしてコンテキスト（プロンプト）を高速に圧縮する、**LLMLingua-2 FastAPI サーバー ＆ macOS メニューバーアプリ**です。

Open WebUI などの LLM クライアントと連携し、長いコンテキストのトークン数を削減して API コストの節約とレスポンスの高速化を実現します。

## ✨ 主な特徴
- 🍏 **Apple Silicon GPU (MPS) 最適化**: Mシリーズチップで高速にモデルを展開・推論。
- ⚡ **FastAPI サーバー内蔵**: バックグラウンドサービス（`brew services`）として常駐可能。
- 🎛️ **柔軟な設定**: 起動用のホスト IP やポート番号を、引数（CLI）および環境変数から動的に変更可能。
- 📦 **Homebrew 互換**: コマンド一発で依存関係（Python 3.11 仮想環境など）を含めて安全にインストール。

---

## 💾 インストール方法

### 1. タップの追加とインストール
```bash
brew tap syuza/mlx-comp https://github.com/syuza/mlx-comp
brew install mlx-comp
```

---

## 🚀 使い方

### 1. 常駐バックグラウンドサーバーとして起動する (推奨)
macOS の `launchd` を利用して、バックグラウンドサービスとしてサーバーを起動します。

```bash
# サービスの開始
brew services start mlx-comp

# サービスの停止
brew services stop mlx-comp

# 起動ログ・エラーの確認
tail -f \$(brew --prefix)/var/log/mlx-comp.log
tail -f \$(brew --prefix)/var/log/mlx-comp.err
```

### 2. メニューバー GUI アプリとして手動起動する
引数なしで実行すると、メニューバーに「LLM」アプリとして起動します。
```bash
mlx-comp
```

---

## ⚙️ 詳細設定（ホストIP・ポートの変更）

`mlx-comp` は以下の優先順位で設定を読み込みます：
**「 起動引数 (最優先) ＞ 環境変数 ＞ デフォルト値 (最優先以下) 」**

| 設定項目 | 起動引数 | 対応環境変数 | デフォルト値 |
| :--- | :--- | :--- | :--- |
| **ホスト IP** | `--host` | `MLX_COMP_HOST` | `0.0.0.0` |
| **ポート番号** | `--port` | `MLX_COMP_PORT` | `8081` |

#### 設定例①：環境変数で指定する場合
```bash
export MLX_COMP_PORT=9000
mlx-comp --server
# 0.0.0 で起動します
```

#### 設定例②：起動引数で上書きする場合 (最優先)
```bash
mlx-comp --server --host 127.0.0.1 --port 9500
# http://127.0.0.1:9500 で起動します
```

---

## 📡 API リファレンス

### プロンプトの圧縮 (`POST /compress`)
FastAPI サーバーへリクエストを送信し、LLMLingua-2 を用いたテキスト圧縮を実行します。

#### クエリ例 (`curl`)
```bash
curl -X POST http://localhost:8081/compress \
     -H "Content-Type: application/json" \
     -d '{
       "text": "これはテスト用の文章です。LLMLingua-2が正常に動作しているかを確認するために、長めのテキストをここに記述しています。不要なトークンが削減され、重要な情報だけが残るかテストします。",
       "rate": 0.5
     }'
```

#### レスポンス例 (`JSON`)
```json
{
  "compressed_text": "圧縮された重要な情報だけのテキスト"
}
```

---

---

## 🤖 Open WebUI との連携方法

本リポジトリに含まれる `openwebui_filter.py` を使用することで、Open WebUI 上での会話や MCP ツールの応答を自動的に圧縮できます。

### 設定手順
1. Open WebUI に管理者（Admin）アカウントでログインします。
2. **「管理者設定」 ＞ 「関数（Functions）」** を開きます。
3. 右上の「＋（プラス）」ボタンを押し、新しい関数を作成します。
4. 本リポジトリの `openwebui_filter.py` のコードを丸ごとコピー＆ペーストして保存します。
5. 作成したフィルターのトグルスイッチを **「有効（Enabled）」** にします。
6. 必要に応じて、Valves 設定から `api_url` や `compression_rate` を調整してください。

---

## 📄 ライセンス
[MIT License](LICENSE)

