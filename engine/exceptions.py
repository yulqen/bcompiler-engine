class MalFormedCSVHeaderException(Exception):
    pass


class NoApplicableSheetsInTemplateFiles(Exception):
    pass


class RemoveFileWithNoSheetRequiredByDatamap(Exception):
    pass