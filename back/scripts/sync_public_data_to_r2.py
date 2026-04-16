#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import mimetypes
import os


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync a local public data directory to a Cloudflare R2 bucket.")
    parser.add_argument("--source", required=True, help="Local directory to upload.")
    parser.add_argument("--bucket", required=True, help="Target R2 bucket name.")
    parser.add_argument("--prefix", default="", help="Optional remote prefix, for example 'data'.")
    parser.add_argument("--account-id", default=os.environ.get("R2_ACCOUNT_ID", ""), help="Cloudflare account ID.")
    parser.add_argument("--access-key-id", default=os.environ.get("R2_ACCESS_KEY_ID", ""), help="R2 access key ID.")
    parser.add_argument("--secret-access-key", default=os.environ.get("R2_SECRET_ACCESS_KEY", ""), help="R2 secret access key.")
    parser.add_argument(
        "--cache-control",
        default="public, max-age=0, s-maxage=86400, stale-while-revalidate=604800",
        help="Cache-Control header applied to uploaded objects.",
    )
    parser.add_argument(
        "--delete-missing",
        action="store_true",
        help="Delete remote objects under the prefix that do not exist locally.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    source_dir = Path(args.source).resolve()
    if not source_dir.exists() or not source_dir.is_dir():
        raise SystemExit(f"Source directory does not exist: {source_dir}")

    if not args.account_id or not args.access_key_id or not args.secret_access_key:
        raise SystemExit("Missing R2 credentials. Provide account ID and access keys via args or environment.")

    try:
        import boto3
        from botocore.config import Config
    except ModuleNotFoundError as exc:
        raise SystemExit("boto3 is required to sync public data to R2.") from exc

    endpoint_url = f"https://{args.account_id}.r2.cloudflarestorage.com"
    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=args.access_key_id,
        aws_secret_access_key=args.secret_access_key,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )

    uploaded_keys: set[str] = set()
    local_files = sorted(path for path in source_dir.rglob("*") if path.is_file())
    if not local_files:
        print(f"No files found under {source_dir}, nothing to upload.")
        return 0

    for file_path in local_files:
        relative_path = file_path.relative_to(source_dir).as_posix()
        remote_key = join_remote_key(args.prefix, relative_path)
        uploaded_keys.add(remote_key)
        extra_args = {
            "ContentType": guess_content_type(file_path),
            "CacheControl": args.cache_control,
        }
        client.upload_file(str(file_path), args.bucket, remote_key, ExtraArgs=extra_args)
        print(f"Uploaded {relative_path} -> s3://{args.bucket}/{remote_key}")

    if args.delete_missing:
        delete_stale_objects(client=client, bucket=args.bucket, prefix=args.prefix, keep_keys=uploaded_keys)

    return 0


def join_remote_key(prefix: str, relative_path: str) -> str:
    normalized_prefix = prefix.strip("/")
    normalized_relative_path = relative_path.strip("/")
    if not normalized_prefix:
        return normalized_relative_path
    if not normalized_relative_path:
        return normalized_prefix
    return f"{normalized_prefix}/{normalized_relative_path}"


def guess_content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".geojson":
        return "application/geo+json; charset=utf-8"
    if suffix == ".json":
        return "application/json; charset=utf-8"

    guessed_type, _ = mimetypes.guess_type(path.name)
    return guessed_type or "application/octet-stream"


def delete_stale_objects(*, client, bucket: str, prefix: str, keep_keys: set[str]) -> None:
    normalized_prefix = prefix.strip("/")
    list_kwargs = {"Bucket": bucket}
    if normalized_prefix:
        list_kwargs["Prefix"] = f"{normalized_prefix}/"

    paginator = client.get_paginator("list_objects_v2")
    stale_keys: list[str] = []
    for page in paginator.paginate(**list_kwargs):
        for item in page.get("Contents", []):
            key = str(item.get("Key") or "")
            if key and key not in keep_keys:
                stale_keys.append(key)

    if not stale_keys:
        return

    for start in range(0, len(stale_keys), 1000):
        chunk = stale_keys[start:start + 1000]
        client.delete_objects(
            Bucket=bucket,
            Delete={"Objects": [{"Key": key} for key in chunk], "Quiet": True},
        )
        for key in chunk:
            print(f"Deleted stale remote object s3://{bucket}/{key}")


if __name__ == "__main__":
    raise SystemExit(main())
