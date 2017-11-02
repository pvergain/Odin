class GraderReadableTypesMixin:
    def get_readable_test_type(self):
        return self.TEST_TYPE_CHOICE[self.test_type][1]

    def get_readable_file_type(self):
        return self.FILE_TYPE_CHOICE[self.file_type][1]
