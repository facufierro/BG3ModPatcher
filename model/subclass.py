import logging


class SubClass:
    def __init__(self, uuid: str, name: str = None):
        self.uuid = uuid
        self.name = "Subclass Name" if name is None else name

    def __str__(self) -> str:
        try:
            return (
                f'<!-- {self.name} -->\n'
                '<node id="SubClass">\n'
                f'  <attribute id="Object" type="guid" value="{self.uuid}"/>\n'
                '</node>'
            )
        except Exception as e:
            logging.error(f"An error occurred while creating SubClass.__str__: {e}")
