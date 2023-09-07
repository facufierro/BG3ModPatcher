
class Progression:
    def __init__(self, uuid, name, table_uuid, level, progression_type, boosts=None, passives_added=None, passives_removed=None, selectors=None, allow_improvement=None, is_multiclass=None, subclasses=None):
        self.uuid = uuid
        self.name = name
        self.table_uuid = table_uuid
        self.level = level
        self.progression_type = progression_type
        self.boosts = boosts if boosts else ""
        self.passives_added = passives_added if passives_added else ""
        self.passives_removed = passives_removed if passives_removed else ""
        self.selectors = selectors if selectors else ""
        self.allow_improvement = allow_improvement if allow_improvement else ""
        self.is_multiclass = is_multiclass if is_multiclass else ""
        self.subclasses = subclasses if subclasses else []

    def __str__(self) -> str:
        optional_attributes = []
        if self.boosts != "":
            optional_attributes.append(self.boosts_string())
        if self.passives_added != "":
            optional_attributes.append(self.passives_added_string())
        if self.passives_removed != "":
            optional_attributes.append(self.passives_removed_string())
        if self.selectors != "":
            optional_attributes.append(self.selectors_string())
        if self.allow_improvement != "":
            optional_attributes.append(self.allow_improvement_string())
        if self.is_multiclass != "":
            optional_attributes.append(self.is_multiclass_string())
        str = (
            f'\n<!-- {self.name} -->\n'
            '<node id="Progression">\n'
            f'  <attribute id="UUID" type="guid" value="{self.uuid}"/>\n'
            f'  <attribute id="Name" type="LSString" value="{self.name}"/>\n'
            f'  <attribute id="TableUUID" type="guid" value="{self.table_uuid}"/>\n'
            f'  <attribute id="Level" type="uint8" value="{self.level}"/>\n'
            f'  <attribute id="ProgressionType" type="uint8" value="{self.progression_type}"/>\n'
            f'{"".join(optional_attributes)}'
            f'{self.subclasses_string()}'
            '</node>'
        )
        return str

    def boosts_string(self) -> str:
        str = (f'\n<attribute id="Boosts" type="LSString" value="{self.boosts}"/>')
        return str

    def passives_added_string(self) -> str:
        str = (f'\n<attribute id="PassivesAdded" type="LSString" value="{self.passives_added}"/>')
        return str

    def passives_removed_string(self) -> str:
        str = (f'\n<attribute id="PassivesRemoved" type="LSString" value="{self.passives_removed}"/>')
        return str

    def selectors_string(self) -> str:
        str = (f'\n<attribute id="Selectors" type="LSString" value="{self.selectors}"/>')
        return str

    def allow_improvement_string(self) -> str:
        str = (f'\n<attribute id="AllowImprovement" type="bool" value="{self.allow_improvement}"/>')
        return str

    def is_multiclass_string(self) -> str:
        str = (f'\n<attribute id="IsMulticlass" type="bool" value="{self.is_multiclass}"/>')
        return str

    def subclasses_string(self) -> str:
        subclass_nodes = ''
        if self.subclasses:
            for subclass in self.subclasses:
                subclass_nodes += f'<!-- {subclass["Name"]} -->\n'
                subclass_nodes += f'<node id="SubClass">\n'
                subclass_nodes += f'  <attribute id="Object" type="guid" value="{subclass["UUID"]}"/>\n'
                subclass_nodes += '</node>\n'
            subclass_nodes = (
                '  <children>\n'
                '    <node id="SubClasses">\n'
                '      <children>\n'
                f'{subclass_nodes}'
                '      </children>\n'
                '    </node>\n'
                '  </children>\n'
            )
        else:
            subclass_nodes = ''
        return subclass_nodes
