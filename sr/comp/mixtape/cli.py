import os.path
import time
from argparse import ArgumentParser
from datetime import timedelta

from ruamel import yaml

from .audio import AudioController
from .magicq import MagicqController
from .mixtape import Mixtape
from .scheduling import Scheduler


def parse_args():
    parser = ArgumentParser(__name__)

    subparsers = parser.add_subparsers(help='Command to run.')

    play = subparsers.add_parser('play', help='Play the mixtape.')
    play.add_argument('mixtape')
    play.add_argument('api')
    play.add_argument('stream')
    play.add_argument(
        '--latency',
        '-l',
        type=int,
        default=950,
        help='In milliseconds.',
    )
    play.add_argument(
        '--audio-backend',
        default='coreaudio',
        help="Audio backend passed to `sox`",
    )
    play.set_defaults(command='play')

    verify = subparsers.add_parser('verify', help='Verify the mixtape.')
    verify.add_argument('mixtape')
    verify.set_defaults(command='verify')

    test = subparsers.add_parser('test', help='Test the mixtape.')
    test.add_argument('mixtape')
    test.set_defaults(command='test')

    return parser.parse_args()


def play(args):
    with open(os.path.join(args.mixtape, 'playlist.yaml')) as file:
        playlist = yaml.safe_load(file)

    magicq_controller = None
    if 'magicq' in playlist:
        config = playlist['magicq']
        magicq_controller = MagicqController((config['host'], config['port']))

    audio_controller = AudioController(args.audio_backend)

    mixtape = Mixtape(args.mixtape, playlist, audio_controller, magicq_controller)

    scheduler = Scheduler(
        api_url=args.api,
        stream_url=args.stream,
        latency=timedelta(seconds=args.latency / 1000),
        generate_actions=mixtape.generate_play_actions,
    )

    scheduler.run()


def verify_tracks(mixtape_dir, tracks):
    for track in tracks:
        try:
            filename = track['filename']
        except KeyError:
            continue
        path = os.path.join(mixtape_dir, filename)
        if not os.path.exists(path):
            print(path, "doesn't exist!")


def verify(args):
    with open(os.path.join(args.mixtape, 'playlist.yaml')) as file:
        playlist = yaml.safe_load(file)

    for num, tracks in playlist['tracks'].items():
        verify_tracks(args.mixtape, tracks)

    verify_tracks(args.mixtape, playlist.get('all', []))


def test(args):
    with open(os.path.join(args.mixtape, 'playlist.yaml')) as file:
        playlist = yaml.safe_load(file)

    config = playlist['magicq']
    magicq_controller = MagicqController((config['host'], config['port']))

    magicq_controller.jump_to_cue(4, 2, 0)
    time.sleep(1)
    # magicq_controller.jump_to_cue(3, 2, 0)


def main():
    args = parse_args()
    if args.command == 'play':
        play(args)
    elif args.command == 'verify':
        verify(args)
    elif args.command == 'test':
        test(args)
