import aioboto3
from botocore.exceptions import ClientError

from app.application.interfaces.services.file_storage import FileStorage


class S3FileStorage(FileStorage):
    def __init__(
        self,
        endpoint_url: str,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        public_url_base: str,
    ) -> None:
        self._endpoint_url = endpoint_url
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket_name = bucket_name
        self._public_url_base = public_url_base.rstrip("/")
        self._session = aioboto3.Session()

    async def upload(
        self,
        file_name: str,
        content: bytes,
        content_type: str,
    ) -> str:
        async with self._session.client(
            "s3",
            endpoint_url=self._endpoint_url,
            aws_access_key_id=self._access_key,
            aws_secret_access_key=self._secret_key,
        ) as client:
            await self._ensure_bucket_exists(client)

            await client.put_object(
                Bucket=self._bucket_name,
                Key=file_name,
                Body=content,
                ContentType=content_type,
            )
            return f"{self._public_url_base}/{file_name}"

    async def _ensure_bucket_exists(self, client) -> None:
        try:
            await client.head_bucket(Bucket=self._bucket_name)
        except ClientError:
            await client.create_bucket(Bucket=self._bucket_name)
