from typing import Any, Optional
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import logging

from aiobotocore.session import get_session
from aiobotocore.client import AioBaseClient

from src.drift_bot.core.base import FileStorage
from src.drift_bot.core.exceptions import (
    UploadingFileError,
    DownloadingFileError,
    RemovingFileError
)


SERVICE_NAME = "s3"


class S3Client(FileStorage):
    def __init__(
            self,
            endpoint_url: str,
            access_key: str,
            secret_key: str,
            secure: bool = False
    ) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = {
            "endpoint_url": endpoint_url,
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "use_ssl": secure,
            "region_name": "us-east-1",
            "service_name": "s3"
        }
        self.session = get_session()

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator[AioBaseClient, Any]:
        async with self.session.create_client(**self.config) as client:
            yield client

    async def create_bucket(self, bucket_name: str) -> None:
        try:
            async with self._get_client() as client:
                await client.create_bucket(Bucket=bucket_name)
            self.logger.info(f"Bucket {bucket_name} created successfully")
        except Exception as e:
            self.logger.error(f"Error while creating bucket: {e}")
            raise RuntimeError(f"Error while creating bucket: {e}") from e

    async def upload_file(
            self,
            file_data: bytes,
            file_name: str,
            bucket_name: str,
            metadata: Optional[dict[str, Any]] = None
    ) -> None:
        kwargs = {"Bucket": bucket_name, "Key": file_name, "Body": file_data}
        if metadata is not None:
            kwargs["ExtraArgs"] = metadata
        try:
            async with self._get_client() as client:
                await client.put_object(**kwargs)
        except Exception as e:
            raise UploadingFileError(f"Error while uploading file: {e}") from e

    async def download_file(self, file_name: str, bucket_name: str) -> bytes:
        try:
            async with self._get_client() as client:
                response = await client.get_object(Bucket=bucket_name, Key=file_name)
                body = response["Body"]
                return await body.read()
        except Exception as e:
            self.logger.error(f"Error while receiving file: {e}")
            raise DownloadingFileError(f"Error while receiving file: {e}") from e

    async def remove_file(self, file_name: str, bucket_name: str) -> str:
        try:
            async with self._get_client() as client:
                await client.delete_object(Bucket=bucket_name, Key=file_name)
            return file_name
        except Exception as e:
            self.logger.error(f"Error while deleting file: {e}")
            raise RemovingFileError(f"Error while deleting file: {e}") from e
