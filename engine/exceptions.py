class MissingSheetFieldError(Exception):
    pass


class MalFormedCSVHeaderException(Exception):
    pass


class NoApplicableSheetsInTemplateFiles(Exception):
    pass


class RemoveFileWithNoSheetRequiredByDatamap(Exception):
    pass


class MissingCellKeyError(Exception):
    pass
