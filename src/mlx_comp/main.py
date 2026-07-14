import os
import argparse
from mlx_comp.server import run_server
from mlx_comp.gui import run_gui

def main():
    parser = argparse.ArgumentParser(description="mlx-comp: LLMLingua-2 Server & GUI App")
    
    # 1. 環境変数を読み込み、なければデフォルト値を設定
    env_host = os.environ.get("MLX_COMP_HOST", "0.0.0.0")
    env_port = int(os.environ.get("MLX_COMP_PORT", "8081"))

    parser.add_argument("--server", action="store_true", help="Run FastAPI server mode")
    
    # 2. default 引数に環境変数の値を指定する
    parser.add_argument("--host", type=str, default=env_host, 
                        help=f"Bind host IP (default: {env_host})")
    parser.add_argument("--port", type=int, default=env_port, 
                        help=f"Bind port number (default: {env_port})")
    
    args = parser.parse_args()

    if args.server:
        run_server(host=args.host, port=args.port)
    else:
        run_gui()

if __name__ == "__main__":
    main()

