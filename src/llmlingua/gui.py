import rumps

class LLMLinguaApp(rumps.App):
    def __init__(self):
        super().__init__("LLM")

    @rumps.menu()
    def about(self):
        rumps.alert("LLMLingua Server", "Running on port 8081")

def run_gui():
    LLMLinguaApp().run()
