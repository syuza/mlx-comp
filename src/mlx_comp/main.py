import os
from mlx_comp.server import run_server

def main():
    # 🍏 起動したら、引数に関係なく全員一律で FastAPI サーバーを起動してポートを開く！
    env_host = os.environ.get("MLX_COMP_HOST", "0.0.0.0")
    env_port = int(os.environ.get("MLX_COMP_PORT", "8081"))
    
    run_server(host=env_host, port=env_port)

if __name__ == "__main__":
    main()
