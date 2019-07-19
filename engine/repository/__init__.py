class Repo:
    "Super class for repository objects."

    def __init__(self, directory_path: str) -> None:
        self.directory_path = directory_path

    def list_as_json(self) -> str:
        raise NotImplementedError("This should be subclassed")
