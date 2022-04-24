import socket, textwrap, json
import struct
from typing import Tuple


class MagicqController:

    def __init__(self, address: Tuple[str, int]) -> None:
        self.address = address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    @staticmethod
    def build_packet(data: bytes) -> bytes:
        length = struct.pack('<H', len(data))
        return b'CREP\0\0\0\0' + length + data

    def send_command_once(self, command: str) -> None:
        self.send_command(command, 1)

    def send_command(self, command: str, retries: int = 5) -> None:
        packet = json.dumps({
            'command': command,
            'retries': retries,
        }).encode()
        self.socket.sendto(packet + b'\n', self.address)

    def activate_playback(self, num: int) -> None:
        self.send_command(f'activate: {num}')

    def release_playback(self, num: int) -> None:
        self.send_command(f'release: {num}')

    def jump_to_cue(self, playback: int, cue_id: int, cue_id_dec: int) -> None:
        self.send_command(f'jump cue: {playback},{cue_id},{cue_id_dec}')
