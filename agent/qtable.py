import pickle
from collections.abc import Hashable
from pathlib import Path
import random
from typing import Any
from environment.direction import Direction

DEFAULT_ACTIONS = tuple(Direction)


class ModelError(Exception):
    pass


class QTable:
    def __init__(
        self,
        actions: tuple[Direction, ...] = DEFAULT_ACTIONS,
        default: float = 0.0,
    ):
        self.actions = actions
        self.default = default
        self.metadata: dict[str, Any] = {}
        self.q: dict = {}

    def get(self, state: Hashable, action: Direction) -> float:
        default_state = {a: self.default for a in self.actions}
        return self.q.get(state, default_state).get(action, 0.0)

    def set(self, state: Hashable, action: Direction, value: float) -> None:
        if state not in self.q:
            self.q[state] = {a: self.default for a in self.actions}
        self.q[state][action] = value

    def best_action(
        self,
        state: Hashable,
        actions: tuple[Direction, ...] | None = None,
    ) -> Direction:
        available_actions = self.actions if actions is None else actions
        state_vals = self.q.get(state, {a: self.default for a in self.actions})
        best_value = max(state_vals[action] for action in available_actions)
        best_actions = tuple(
            action
            for action in available_actions
            if state_vals[action] == best_value
        )
        return random.choice(best_actions)

    def save(self, path: str | Path) -> None:
        model_path = Path(path)
        try:
            model_path.parent.mkdir(parents=True, exist_ok=True)
            with model_path.open("wb") as f:
                pickle.dump(
                    {
                        "version": 1,
                        "actions": self.actions,
                        "metadata": self.metadata,
                        "q": self.q,
                    },
                    f,
                )
        except (OSError, TypeError, ValueError) as error:
            raise ModelError(
                f"Unable to save model '{model_path}': {error}"
            ) from error

    @classmethod
    def load(cls, path: str | Path) -> "QTable":
        model_path = Path(path)
        try:
            with model_path.open("rb") as f:
                model = pickle.load(f)
            table = cls(actions=model["actions"])
            table.metadata = model.get("metadata", {})
            table.q = model.get("q", {})
            return table
        except (
            OSError,
            EOFError,
            pickle.UnpicklingError,
            AttributeError,
            KeyError,
            IndexError,
            ImportError,
            TypeError,
            ValueError,
        ) as error:
            raise ModelError(
                f"Unable to load model '{model_path}': {error}"
            ) from error
