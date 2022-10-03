class FileValidateError(Exception):
    def __init__(self, error_massage):
        self.__error_massage = error_massage

    def __str__(self):
        return self.__error_massage


class ExecCommandError(Exception):
    def __init__(self, error_massage):
        self.__error_massage = error_massage

    def __str__(self):
        return self.__error_massage
