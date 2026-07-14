class MlxComp < Formula
  desc "LLMLingua-2 FastAPI server with macOS Menu Bar app"
  version "0.1.0"

  # 本番環境
  #url "https://github.com/syuza/llmlingua/archive/refs/tags/v0.1.0.tar.gz"
  #sha256 "8b4028b8de36742bca2fb63ee82aa3c653645dd3f4c4e65e6ce6b579f5acd289"

  # 開発環境
  url "file:///Users/syuza/Developer/genAI/mlx-comp"
  license "MIT"

  depends_on "python@3.11"

  # Homebrew標準のPython仮想環境ヘルパーを読み込む
  include Language::Python::Virtualenv

  def install
    # 🌟 追加：手元の開発フォルダの中身を、Homebrewのビルド環境へ強制的に直接コピーする
    cp_r Dir["/Users/syuza/Developer/genAI/mlx-comp/*"], buildpath

    # 1. 依存ライブラリのバイナリ破損を防ぐための環境変数
    ENV["LDFLAGS"] = "-Wl,-headerpad_max_install_names"
    ENV["RUSTFLAGS"] = "-C link-arg=-Wl,-headerpad_max_install_names"
    ENV["CARGO_PROFILE_RELEASE"] = "false"

    # 2. Python 3.11 の実行パスを取得
    python3 = Formula["python@3.11"].opt_bin/"python3.11"

    # 3. 明示的に libexec フォルダへ仮想環境を作成
    system python3, "-m", "venv", libexec

    # 4. 仮想環境内の pip と tools を最新にする
    system libexec/"bin/pip", "install", "--upgrade", "pip", "setuptools", "wheel"

    # 5. 各パッケージをソース（--no-binary）からインストール
    system libexec/"bin/pip", "install", "--no-binary", "pydantic-core,rpds-py,tiktoken",
           "fastapi", "uvicorn", "pydantic", "llmlingua", "rumps"

    # 6. 自分自身（buildpath = カレントディレクトリ）をインストール
    system libexec/"bin/pip", "install", buildpath

    # 7. 実行用のラッパースクリプトを作成して bin へ配置
    # (bin オブジェクトのメソッドとして正しく呼び出します)
    bin.write_env_script libexec/"bin/python", {}

  end

  def caveats
    <<~EOS
      mlx-comp installed via Homebrew.

      Commands:
        mlx-comp # Launch Menu Bar GUI app
        mlx-comp --server # Run FastAPI server in background via brew services

      Service Management:
        brew services start mlx-comp # Start background server
        brew services stop mlx-comp # Stop background server

      Logs:
        tail -f #{var}/log/mlx-comp.err  # View error logs
    EOS
  end

  service do
    run ["#{libexec}/bin/python", "-m", "mlx_comp.main", "--server"]
    keep_alive true
    log_path var/"log/mlx-comp.log"
    error_log_path var/"log/mlx-comp.err" # error_log から error_log_path に修正（API仕様準拠）
  end
end

