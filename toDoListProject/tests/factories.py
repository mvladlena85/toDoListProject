import factory
from django.utils import timezone
from pytest_factoryboy import register

from toDoListProject.core.models import User
from toDoListProject.goals.models import Board, BoardParticipant, GoalCategory, Goal


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
    created = factory.LazyFunction(timezone.now)
    updated = factory.LazyFunction(timezone.now)

    class Meta:
        abstract = True


@register
class BoardFactory(DatesFactoryMixin):
    title = factory.Faker('word')

    class Meta:
        model = Board


@register
class BoardParticipantFactory(DatesFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = BoardParticipant


@register
class CategoryFactory(DatesFactoryMixin):
    board = factory.SubFactory(BoardFactory)
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('word')

    class Meta:
        model = GoalCategory


@register
class GoalFactory(DatesFactoryMixin):
    title = factory.Faker('word')
    category = factory.SubFactory(CategoryFactory)
    description = factory.Faker('sentence')
    user = factory.SubFactory(UserFactory)
    status = factory.Faker('random_element', elements=[Goal.Status.to_do, Goal.Status.in_progress, Goal.Status.done])
    priority = factory.Faker('random_element', elements=[x[0] for x in Goal.Priority.choices])
    due_date = factory.Faker('date_time_this_month', before_now=False, after_now=True)

    class Meta:
        model = Goal
