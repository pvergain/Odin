import factory

from odin.common.faker import faker
from odin.users.factories import BaseUserFactory

from .models import Student, Teacher, Course, CourseAssignment


class StudentFactory(BaseUserFactory):
    class Meta:
        model = Student


class TeacherFactory(BaseUserFactory):
    class Meta:
        model = Teacher


class CourseFactory(factory.DjangoModelFactory):
    name = factory.LazyAttribute(lambda _: faker.word())
    start_date = factory.LazyAttribute(lambda _: faker.date())
    end_date = factory.LazyAttribute(lambda _: faker.date())

    repository = factory.LazyAttribute(lambda _: faker.url())
    video_channel = factory.LazyAttribute(lambda _: faker.url())
    facebook_group = factory.LazyAttribute(lambda _: faker.url())

    class Meta:
        model = Course


class CourseAssignmentStudentFactory(factory.DjangoModelFactory):
    student = factory.SubFactory(StudentFactory)
    course = factory.SubFactory(CourseFactory)

    class Meta:
        model = CourseAssignment


class CourseAssignmentTeacherFactory(factory.DjangoModelFactory):
    teacher = factory.SubFactory(TeacherFactory)
    course = factory.SubFactory(CourseFactory)

    class Meta:
        model = CourseAssignment


class CourseWithStudentCourseAssignmentFactory(CourseFactory):
    """
    Creates a CourseAssignment as a post generation hook and
    attaches an existing Student to the course.
    """
    course_assignment = factory.RelatedFactory(CourseAssignmentStudentFactory, 'course')


class CourseWithTeacherCourseAssignmentFactory(CourseFactory):
    """
    Creates a CourseAssignment as a post generation hook and
    attaches an existing Teacher to the Course.
    """
    course_assignment = factory.RelatedFactory(CourseAssignmentTeacherFactory, 'course')
