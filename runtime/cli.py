import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="snake",
        description="Learn2Slither - snake reinforcement training.",
    )
    parser.add_argument(
        "--map-size",
        "-map-size",
        type=int,
        default=10,
        dest="map_size",
        help="Size of the map (square).",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--train",
        action="store_true",
        help="Train the Q-learning agent without opening a window.",
    )
    mode.add_argument(
        "--view",
        action="store_true",
        help="Display a trained model playing by itself.",
    )
    parser.add_argument(
        "--episodes",
        type=int,
        default=1000,
        help="Number of training episodes.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=500,
        dest="max_steps",
        help="Maximum number of steps per episode.",
    )
    parser.add_argument(
        "--load-model",
        metavar="PATH",
        help="Load a Q-table before training.",
    )
    parser.add_argument(
        "--save-model",
        metavar="PATH",
        help="Save the Q-table after training.",
    )
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if not (5 <= args.map_size <= 100):
        raise ValueError("The size of the map must be between 5 and 100")
    if args.episodes < 1:
        raise ValueError("The number of episodes must be positive")
    if args.max_steps < 1:
        raise ValueError("The maximum number of steps must be positive")
    if args.save_model and not args.train:
        raise ValueError("--save-model requires --train")
    if args.view and args.load_model is None:
        raise ValueError("--view requires --load-model")
