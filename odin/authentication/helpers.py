import boto3
import uuid


def start_s3_client(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    aws_s3_region_name: str,
):

    config = boto3.session.Config(region_name=aws_s3_region_name)

    s3 = boto3.client(
        's3',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        config=config
    )

    return s3


def get_presigned_post(
    s3: boto3.client,
    s3_bucket: str,
    file_type: str,
):

    new_file_name = uuid.uuid4().hex

    presigned_post = s3.generate_presigned_post(
        Bucket=s3_bucket,
        Key=f'media/{new_file_name}',
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[
            {"acl": "public-read"},
            {"Content-Type": file_type}
        ],
        ExpiresIn=3600
    )

    upload_data = {
       'data': presigned_post,
       'url': f'https://{s3_bucket}.s3.amazonaws.com/media/{new_file_name}',
       'file_name': new_file_name
    }

    return upload_data
