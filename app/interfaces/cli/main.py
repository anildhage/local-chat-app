import argparse
from pathlib import Path

from app.core.config import load_config, set_active_model, set_active_profile
from app.core.logger import get_logger
from app.core.model_service import get_client
from app.core.chat_service import ChatService


def print_help() -> None:
    print("Available commands:")
    print("  /help                Show this help text")
    print("  /bye                 Exit interactive chat")
    print("  /list-models         Show running Ollama models")
    print("  /offload <model>     Unload a running Ollama model")
    print("  /model <name>        Switch active chat model and persist it")
    print("  /model <name> <embedding>  Switch active chat and embedding models")
    print("  /status              Show active profile and model info")
    print("  /exit, /quit         Exit interactive chat")
    print("")
    print("Examples:")
    print("  /list-models")
    print("  /offload qwen2.5-coder:1.5b")
    print("  /model qwen2.5-coder:1.5b")
    print("  /model qwen2.5-coder:1.5b qwen2.5-coder:1.5b")


def main() -> None:
    parser = argparse.ArgumentParser(description="Local chat app CLI")
    parser.add_argument("command", choices=["chat", "search", "index", "config"], help="Command to run")
    parser.add_argument("query", nargs="?", help="User query for chat or search")
    parser.add_argument("--profile", help="Override active model profile for this run")
    parser.add_argument("--top-k", type=int, default=5, help="Number of search results")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--set-profile", help="Persistently set the active profile in config")
    parser.add_argument("--set-model", help="Persistently set the active chat model in config")
    parser.add_argument("--set-embedding-model", help="Persistently set the active embedding model in config")
    args = parser.parse_args()

    config = load_config()
    if args.profile:
        profile = config.get("profiles", {}).get(args.profile)
        if profile:
            config.update(profile)
            config["active_profile"] = args.profile
        else:
            raise ValueError(f"Unknown profile: {args.profile}")

    if args.set_profile:
        config = set_active_profile(args.set_profile)
    elif args.set_model:
        config = set_active_model(args.set_model, args.set_embedding_model)

    config["debug"] = args.debug
    logger = get_logger(debug=args.debug)
    client = get_client(config)
    service = ChatService(config, client)

    if args.command == "index":
        result = service.index_notes()
        logger.info("Indexed %d chunks.", len(result.get("chunks", [])))
    elif args.command == "chat":
        def run_chat(prompt: str) -> None:
            answer = service.chat(prompt)
            print(f"Zapp: {answer['answer']}")
            if args.debug:
                logger.debug("Sources: %s", answer["sources"])

        def offload_model(model_name: str) -> None:
            if not model_name:
                print("Usage: /offload <model>")
                return
            success = client.stop_model(model_name)
            if success:
                print(f"Offloaded model: {model_name}")
            else:
                print(f"Failed to offload model: {model_name}")

        def offload_all_models() -> None:
            running = client.list_running_models()
            if not running:
                print("No running models to offload.")
                return
            stopped = []
            for model_name in running:
                if client.stop_model(model_name):
                    stopped.append(model_name)
            if stopped:
                print("Offloaded models:")
                for model_name in stopped:
                    print(f"  {model_name}")
            else:
                print("Failed to offload running models.")

        def switch_model(model_name: str, embedding_model: str | None = None) -> None:
            if not model_name:
                print("Usage: /model <name> [embedding_model]")
                return
            running = client.list_running_models()
            if running:
                print("Offloading currently running models before activating the new model...")
                offload_all_models()
            try:
                new_config = set_active_model(model_name, embedding_model)
                service.config = new_config
                print(f"Active chat model updated to: {new_config['chat_model']}")
                print(f"Active embedding model updated to: {new_config['embedding_model']}")
            except ValueError as exc:
                print(f"Error switching model: {exc}")

        def print_status() -> None:
            print(f"Active profile: {config.get('active_profile')}")
            print(f"Chat model: {config.get('chat_model')}")
            print(f"Embedding model: {config.get('embedding_model')}")
            running = client.list_running_models()
            if running:
                print("Running models:")
                for model_name in running:
                    print(f"  {model_name}")
            else:
                print("No running models.")

        if args.query:
            run_chat(args.query)
        else:
            print("Interactive chat mode. Type '/help' for commands, or '/bye' to stop.")
            while True:
                try:
                    prompt = input("BotZapp> ").strip()
                except (KeyboardInterrupt, EOFError):
                    print()
                    break
                if not prompt:
                    continue
                normalized = prompt.lower()
                if normalized in {"exit", "quit", "/bye"}:
                    break
                if normalized == "/help":
                    print_help()
                    continue
                if normalized == "/list-models":
                    available = client.list_available_models()
                    running = set(client.list_running_models())
                    if available:
                        print("Available models:")
                        for model_name in available:
                            flags = []
                            if model_name == config.get("chat_model"):
                                flags.append("active")
                            if model_name in running:
                                flags.append("running")
                            suffix = f" ({', '.join(flags)})" if flags else ""
                            print(f"  {model_name}{suffix}")
                    else:
                        print("No installed models found.")
                    continue
                if normalized == "/list-running":
                    running = client.list_running_models()
                    if running:
                        print("Running models:")
                        for model_name in running:
                            print(f"  {model_name}")
                    else:
                        print("No running models found.")
                    continue
                if normalized == "/offload-all":
                    offload_all_models()
                    continue
                if normalized.startswith("/offload"):
                    parts = prompt.split(maxsplit=1)
                    offload_model(parts[1].strip() if len(parts) > 1 else "")
                    continue
                if normalized.startswith("/model"):
                    parts = prompt.split(maxsplit=2)
                    model_name = parts[1].strip() if len(parts) > 1 else ""
                    embedding_model = parts[2].strip() if len(parts) > 2 else None
                    switch_model(model_name, embedding_model)
                    continue
                if normalized == "/status":
                    print_status()
                    continue
                run_chat(prompt)
    elif args.command == "search":
        if not args.query:
            raise ValueError("Query is required for search")
        results = service.search(args.query, top_k=args.top_k)
        for item in results:
            logger.info("%s", item["path"])
    elif args.command == "config":
        logger.info("Active profile: %s", config.get("active_profile"))
        logger.info("Chat model: %s", config.get("chat_model"))
        logger.info("Embedding model: %s", config.get("embedding_model"))


if __name__ == "__main__":
    main()
