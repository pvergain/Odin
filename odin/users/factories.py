import factory

from odin.common.faker import faker

from .models import Profile, BaseUser


class BaseUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = BaseUser

    email = factory.Sequence(lambda n: '{}{}'.format(n, faker.email()))
    password = faker.password()


class SuperUserFactory(BaseUserFactory):
    """
    Taken from:
    <http://factoryboy.readthedocs.io/en/latest/recipes.html#custom-manager-methods>
    """
    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)

        return manager.create_superuser(*args, **kwargs)


class ProfileFactory(factory.DjangoModelFactory):
    full_name = factory.LazyAttribute(lambda _: faker.name())
    description = factory.LazyAttribute(lambda _: faker.text())

    class Meta:
        model = Profile
