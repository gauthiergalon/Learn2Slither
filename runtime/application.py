from agent.agent import Agent
from agent.qtable import ModelError
from agent.trainer import Trainer
from environment.game import Game
from runtime.cli import build_parser, validate_args


def run_training(
    map_size: int,
    episodes: int,
    max_steps: int,
    load_model: str | None = None,
    save_model: str | None = None,
) -> None:
    trainer = Trainer(map_size, max_steps=max_steps)
    if load_model is not None:
        trainer.load_model(load_model)

    stats = trainer.train(episodes)
    if save_model is not None:
        trainer.save_model(save_model)

    print(
        f"Training complete: {stats.episodes} episodes, "
        f"average reward={stats.average_reward:.2f}, "
        f"best length={stats.best_score}, "
        f"states={len(trainer.qtable.q)}"
    )
    if save_model is not None:
        print(f"Model saved to {save_model}")


def run_view(
    map_size: int,
    max_steps: int,
    model_path: str,
    step_by_step: bool = False,
) -> None:
    agent = Agent(training=False)
    agent.load_model(model_path)
    game = Game(
        map_size,
        agent=agent,
        max_steps=max_steps,
        step_by_step=step_by_step,
    )
    try:
        game.run_episode()
    finally:
        game.close()


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        validate_args(args)
    except ValueError as error:
        parser.error(str(error))

    try:
        if args.train:
            run_training(
                args.map_size,
                args.episodes,
                args.max_steps,
                args.load_model,
                args.save_model,
            )
        elif args.view:
            run_view(
                args.map_size,
                args.max_steps,
                args.load_model,
                args.step,
            )
    except ModelError as error:
        parser.error(str(error))
