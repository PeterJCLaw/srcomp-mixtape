import subprocess


class AudioController:

    def __init__(self, audio_backend: str) -> None:
        self.audio_backend = audio_backend

    def play(
        self,
        filename: str,
        output_device: str,
        trim_start: float,
    ) -> 'subprocess.Popen[bytes]':
        print('Playing', filename)
        args = ['totem', filename]
        return subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
