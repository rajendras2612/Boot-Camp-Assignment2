import argparse
from pathlib import Path

from huggingface_hub import HfApi, Repository, create_repo, upload_folder


def parse_args():
    parser = argparse.ArgumentParser(description="Publish a model or artifact folder to Hugging Face Hub.")
    parser.add_argument("--repo-id", required=True, help="Hugging Face repo id, e.g. username/model-name")
    parser.add_argument(
        "--path",
        default=".",
        help="Local directory that contains the model artifact or files to publish.",
    )
    parser.add_argument("--token", default=None, help="Hugging Face access token.")
    parser.add_argument(
        "--private",
        action="store_true",
        help="Create the repo as private if it does not exist.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    folder = Path(args.path).expanduser().resolve()

    if not folder.exists() or not folder.is_dir():
        raise SystemExit(f"Path does not exist or is not a directory: {folder}")

    token = args.token or os.environ.get("HF_TOKEN")
    if not token:
        raise SystemExit("Hugging Face token required via --token or HF_TOKEN environment variable.")

    api = HfApi(token=token)
    try:
        create_repo(repo_id=args.repo_id, token=token, private=args.private, exist_ok=True)
    except Exception as error:
        print(f"Could not create or validate repo: {error}")

    print(f"Publishing {folder} to Hugging Face repo {args.repo_id}...")
    upload_folder(
        folder_path=folder,
        path_in_repo="",
        repo_id=args.repo_id,
        token=token,
        repo_type="model",
    )
    print("Publish complete.")


if __name__ == "__main__":
    import os

    main()
