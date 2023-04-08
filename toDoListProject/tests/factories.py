import factory
from django.utils import timezone
from pytest_factoryboy import register

from toDoListProject.core.models import User
from toDoListProject.goals.models import Board


@register
class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Faker('user_name')
    password = factory.Faker('password')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('ascii_email')

    class Meta:
        model = User

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._get_manager(model_class).create_user(*args, **kwargs)


class DatesFactoryMixin(factory.django.DjangoModelFactory):
    created = factory.LazyFunction(timezone.now())
    updated = factory.LazyFunction(timezone.now())

    class Meta:
        abstract = True


@register
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('word')

    class Meta:
        model = Board
