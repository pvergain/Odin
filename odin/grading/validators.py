from django.core.validators import URLValidator


def validate_url(url):
    validator = URLValidator()
    try:
        validator(url)
    except ValidationError:
        raise ValidationError(f'{url} is not a valid url.')


def validate_github_url(url):
    validate_url(url)

    github_domain = "github.com"
    split_url = url.split('/')

    if github_domain not in split_url:
        raise ValidationError(f'{url} is not a valid url.')
