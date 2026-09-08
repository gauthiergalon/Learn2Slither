# Entry point: delegates to runtime application
import sys

from runtime.application import main as run_application


def main() -> None:
    run_application()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOpération interrompue.", file=sys.stderr)
        raise SystemExit(130)
