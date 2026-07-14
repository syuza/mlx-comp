class Llmlingua < Formula
  desc "LLMLingua-2 FastAPI server with macOS Menu Bar app"
  homepage "https://github.com/yourusername/llmlingua" # あなたのGitHub URLに書き換えてください
  version "0.1.0"

  # GitHubのリリースから取得する場合の設定例
  url "https://github.com/yourusername/llmlingua/archive/refs/tags/v#{version}.tar.gz"
  sha256 "fef5b0c918488ccb141807c135191bb4df4bbfed75ae9d2ee3486afe36a95877" # shasum -a 256 で取得した値を入力
  license "MIT"

  depends_on "python@3.11"

  # macOS 27 beta's `strip` corrupts dynamic offsets in Mach-O libraries
  # venv内のバイナリがHomebrewのクリーンアップで壊されるのを防ぐ
  on_macos do
    skip_clean "libexec" if MacOS.version >= "27"
  end

  def install
    # 1. libexec内に仮想環境を作成
    system "python3.11", "-m", "venv", libexec

    # 2. ビルド設定: Mach-Oの再配置（relocation）を許可するためにheaderpadを付与
    ENV.append "LDFLAGS", "-Wl,-headerpad_max_install_names"
    ENV.append "RUSTFLAGS", "-C link-arg=-Wl,-headerpad_max_install_names"

    # macOS 27対策: ソースビルドを強制し、strip（バイナリ削減）による破損を防ぐ
    # pydantic-core, tokenizersなどはバイナリ配布版だとdlopenに失敗することがあるため
    no_binary = "pydantic-core,tokenizers"
    pip_flags = []
    if MacOS.version >= "27"
      no_binary += ",rpds-py,tiktoken"
      ENV["CARGO_PROFILE_RELEASE_STRIP"] = "false"
      pip_flags << "--no-cache-dir"
    end

    # 3. pipを使用して依存関係をインストール
    pip_install = [libexec/"bin/pip", "install", *pip_flags, "--no-binary", no_binary]
    
    # プロジェクトのインストール (pyproject.tomlを使用)
    system(*pip_install, ".")

    # 4. コマンドライン用のシンボリックリンクを作成
    # GUIモードとサーバーモードを引数で切り替える設計にするため、エントリーポイントはmain.pyとする
    # ここでは 'llmlingua' コマンドを作成
    bin.install_symlink libexec/"bin/python", "llmlingua"
    # サーバー専用のラッパーコマンドを作成（brew services用）
    bin.install_symlink libexec/"bin/python", "llmlingua-server"
  end

  # brew services 用の定義
  # 引数に "--server-only" を渡すことで、GUI（rumps）を起動せずにバックグラウンド実行させる
  service do
    run [bin/"llmlingua", "--server-only"]
    keep_alive true
    working_dir Dir.pwd
    log_path var/"log/llmlingua.log"
    error_log_path var/"log/llmlingua.err"
  end

  test do
    # インストールされたコマンドがバージョンを返せるか確認
    assert_match version.to_s, shell_output("#{bin}/llmlingua --version")
  end
end
