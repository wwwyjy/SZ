#inerleaver:mic，text, socket。interact_type:1、语音/文字交互；
class Interact:

    def __init__(self, interleaver: str, interact_type: int, data: dict):
        self.interleaver = interleaver
        self.interact_type = interact_type
        self.data = data
