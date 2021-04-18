class FilterLabel:
    label: str
    ignore_case: bool

    def __init__(self, label: str, ignore_case: bool = False):
        self.label = label
        self.ignore_case = ignore_case
