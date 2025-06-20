

class RanOutNumbersError(Exception):
    """Закончились доступные номера для регистрации"""
    pass


class FileStorageError(Exception):
    pass


class UploadingFileError(FileStorageError):
    pass


class DownloadingFileError(FileStorageError):
    pass


class RemovingFileError(FileStorageError):
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


class ServiceError(Exception):
    pass


class CodeExpiredError(ServiceError):
    """Истёк реферальный код."""
    pass
