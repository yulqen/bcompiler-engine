class DatamapNotCSVException(Exception):
    pass


class NestedZipError(Exception):
    pass


class MissingSheetFieldError(Exception):
    pass


class MalFormedCSVHeaderException(Exception):
    pass


class MalFormedCSVEmptyTailRowsException(Exception):
    pass


class NoApplicableSheetsInTemplateFiles(Exception):
    pass


class RemoveFileWithNoSheetRequiredByDatamap(Exception):
    pass


class MissingCellKeyError(Exception):
    pass


class DatamapFileEncodingError(Exception):
    pass


class MissingLineError(Exception):
    pass
