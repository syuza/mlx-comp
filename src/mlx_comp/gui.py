import rumps

class MlxCompApp(rumps.App):
    def __init__(self):
        # メニューバーに表示されるタイトルアイコン/テキスト
        super().__init__("LLM")

    @rumps.clicked("About")
    def about(self, sender):  # rumpsのイベントハンドラは第2引数(sender)が必要です
        rumps.alert("MLX Comp Server", "Running on port 8081")

def run_gui():
    MlxCompApp().run()

