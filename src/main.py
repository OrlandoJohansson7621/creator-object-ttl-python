import argparse
from datetime import timedelta
from .infrai_client import InfraiClient
from .creator_ttl_service import run_sweep


def main() -> None:
    parser = argparse.ArgumentParser(description="Sweep expired creator-commerce objects")
    parser.add_argument("--bucket", default="creator-throwaways")
    parser.add_argument("--ttl-hours", type=int, default=24)
    args = parser.parse_args()
    client = InfraiClient()
    client.create_bucket(args.bucket)
    removed = run_sweep(client, args.bucket, timedelta(hours=args.ttl_hours))
    print({"bucket": args.bucket, "removed": removed, "ttl_hours": args.ttl_hours})


if __name__ == "__main__":
    main()

