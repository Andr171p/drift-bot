

class RanOutNumbersError(Exception):
    """Закончились доступные номера для регистрации"""
    pass


class UploadingFileError(Exception):
    pass


class DownloadingFileError(Exception):
    pass


class RemovingFileError(Exception):
    pass


class RepositoryError(Exception):
    pass


class CreationError(RepositoryError):
    pass


class ReadingError(RepositoryError):
    pass


class UpdatingError(RepositoryError):
    pass


class DeletingError(RepositoryError):
    pass

