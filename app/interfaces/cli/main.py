import argparse
from pathlib import Path

from app.core.config import load_config, set_active_model, set_active_profile
from app.core.logger import get_logger
from app.core.model_service import get_client
from app.core.chat_service import ChatService


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
        if not args.query:
            raise ValueError("Query is required for chat")
        answer = service.chat(args.query)
        logger.info("Answer:\n%s", answer["answer"])
        if args.debug:
            logger.debug("Sources: %s", answer["sources"])
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
