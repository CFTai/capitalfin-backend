from storages.backends import s3boto3


class MediaStorage(s3boto3.S3Boto3Storage):
    file_overwrite = False
