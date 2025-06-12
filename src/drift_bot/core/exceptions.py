

class RanOutNumbersError(Exception):
    """Закончились доступные номера для регистрации"""
    pass


class UploadingFileError(Exception):
    pass


class DownloadingFileError(Exception):
    pass


class RemovingFileError(Exception):
    pass
