import six
import environ

env = environ.Env()

AWS_ACCESS_KEY_ID = env('DJANGO_AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('DJANGO_AWS_SECRET_ACCESS_KEY')
AWS_S3_REGION_NAME = env('DJANGO_AWS_S3_REGION')
AWS_STORAGE_BUCKET_NAME = env('DJANGO_AWS_STORAGE_BUCKET_NAME')

AWS_S3_HOST = env('DJANGO_AWS_S3_HOST', default='s3-%s.amazonaws.com' % AWS_S3_REGION_NAME)
AWS_S3_SIGNATURE_VERSION = env('DJANGO_AWS_S3_SIGNATURE_VERSION', default='s3v4')

"""
Setting AWS_QUERYSTRING_AUTH to False to remove query parameter authentication from generated URLs. This can be useful if your S3 buckets are public.
"""
AWS_QUERYSTRING_AUTH = False

"""
By default files with the same name will overwrite each other. Set this to False to have extra characters appended.
"""
AWS_S3_FILE_OVERWRITE = False

AWS_EXPIRY = 60 * 60 * 24 * 7
AWS_S3_OBJECT_PARAMETERS = {
    f'CacheControl': 'max-age={AWS_EXPIRY}',
}
