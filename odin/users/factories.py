import factory

from odin.common.faker import faker

from .models import Profile, BaseUser


class BaseUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = BaseUser

    email = factory.Sequence(lambda n: '{}{}'.format(n, faker.email()))
    password = faker.password()


class ProfileFactory(factory.DjangoModelFactory):
    full_name = factory.LazyAttribute(lambda _: factory.name())

    class Meta:
        model = Profile
