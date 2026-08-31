import argparse

from app.agent import SupportAgent


def main():
    parser = argparse.ArgumentParser(
        description="Aster & Row AI Support Agent"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show retrieval and tool traces.",
    )

    args = parser.parse_args()

    agent = SupportAgent()

    print("=" * 60)
    print("ASTER & ROW AI SUPPORT AGENT")
    print("Type 'exit' to quit.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        result = agent.handle(user_input)

        print("\nAgent:")
        print(result["answer"])

        if result["sources"]:
            print("\nSources:")
            for source in result["sources"]:
                print(
                    f"- {source['filename']} | "
                    f"{source['heading']}"
                )

        if result["handoff"]:
            print("\n[Human support recommended]")

        if args.debug:
            print("\n--- DEBUG TRACE ---")
            print(result["debug"])


if __name__ == "__main__":
    main()
