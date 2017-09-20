from django.conf import settings

from storages.backends.s3boto3 import S3Boto3Storage

# class MediaStorage(S3Boto3Storage):
#     location = settings.MEDIA_LOCATION
#     custom_domain = settings.MEDIA_S3_CUSTOM_DOMAIN


class StaticStorage(S3Boto3Storage):
    location = settings.STATIC_LOCATION
    custom_domain = settings.STATIC_CDN_CUSTOM_DOMAIN
