from datetime import date


class CorePrompt:
    def __init__(self):
        self._today = date.today().strftime("%B-%d-%Y")

    def _get_system_prompt(self) -> str:
        return (
            "You are a highly intelligent AI Virtual Assistant for the "
        )