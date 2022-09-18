# -*- coding: utf-8 -*-
"""Run-time objects."""

try:
  import __builtin__ as builtins
except ImportError:
  import builtins

import keyword
import sys

from dtfabric import data_types
from dtfabric import definitions


class StructureValuesClassFactory(object):
  """Structure values class factory."""

  _CLASS_TEMPLATE = '\n'.join([
      'class {type_name:s}(object):',
      '  """{type_description:s}.',
      '',
      '  Attributes:',
      '{class_attributes_description:s}',
      '  """',
      '',
      '  def __init__(self, {init_arguments:s}):',
      '    """Initializes an instance of {type_name:s}."""',
      '    super({type_name:s}, self).__init__()',
      '{instance_attributes:s}',
      ''])

  _PYTHON_NATIVE_TYPES = {
      definitions.TYPE_INDICATOR_BOOLEAN: 'bool',
      definitions.TYPE_INDICATOR_CHARACTER: 'str',
      definitions.TYPE_INDICATOR_FLOATING_POINT: 'float',
      definitions.TYPE_INDICATOR_INTEGER: 'int',
      definitions.TYPE_INDICATOR_STREAM: 'bytes',
      definitions.TYPE_INDICATOR_STRING: 'str',
      definitions.TYPE_INDICATOR_UUID: 'uuid.UUID'}

  @classmethod
  def _CreateClassTemplate(cls, data_type_definition):
    """Creates the class template.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      str: class template.
    """
    type_name = data_type_definition.name

    type_description = data_type_definition.description or type_name
    while type_description.endswith('.'):
      type_description = type_description[:-1]

    class_attributes_description = []
    init_arguments = []
    instance_attributes = []

    for member_definition in data_type_definition.members:
      attribute_name = member_definition.name

      description = member_definition.description or attribute_name
      while description.endswith('.'):
        description = description[:-1]

      member_data_type = getattr(member_definition, 'member_data_type', '')
      if isinstance(member_definition, data_types.MemberDataTypeDefinition):
        member_definition = member_definition.member_data_type_definition

      member_type_indicator = member_definition.TYPE_INDICATOR
      if member_type_indicator == definitions.TYPE_INDICATOR_SEQUENCE:
        element_type_indicator = member_definition.element_data_type
        member_type_indicator = f'tuple[{element_type_indicator:s}]'
      else:
        member_type_indicator = cls._PYTHON_NATIVE_TYPES.get(
            member_type_indicator, member_data_type)

      argument = f'{attribute_name:s}=None'
      definition = f'    self.{attribute_name:s} = {attribute_name:s}'
      description = (
          f'    {attribute_name:s} ({member_type_indicator:s}): '
          f'{description:s}.')

      class_attributes_description.append(description)
      init_arguments.append(argument)
      instance_attributes.append(definition)

    class_attributes_description = '\n'.join(
        sorted(class_attributes_description))
    init_arguments = ', '.join(init_arguments)
    instance_attributes = '\n'.join(sorted(instance_attributes))

    template_values = {
        'class_attributes_description': class_attributes_description,
        'init_arguments': init_arguments,
        'instance_attributes': instance_attributes,
        'type_description': type_description,
        'type_name': type_name}

    return cls._CLASS_TEMPLATE.format(**template_values)

  @classmethod
  def _IsIdentifier(cls, string):
    """Checks if a string contains an identifier.

    Args:
      string (str): string to check.

    Returns:
      bool: True if the string contains an identifier, False otherwise.
    """
    return (
        string and not string[0].isdigit() and
        all(character.isalnum() or character == '_' for character in string))

  @classmethod
  def _ValidateDataTypeDefinition(cls, data_type_definition):
    """Validates the data type definition.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      ValueError: if the data type definition is not considered valid.
    """
    if not cls._IsIdentifier(data_type_definition.name):
      raise ValueError(
          f'Data type definition name: {data_type_definition.name!s} not '
          f'a valid identifier')

    if keyword.iskeyword(data_type_definition.name):
      raise ValueError(
          f'Data type definition name: {data_type_definition.name!s} matches '
          f'keyword')

    members = getattr(data_type_definition, 'members', None)
    if not members:
      raise ValueError(
          f'Data type definition name: {data_type_definition.name!s} missing '
          f'members')

    defined_attribute_names = set()

    for member_definition in members:
      attribute_name = member_definition.name

      if not cls._IsIdentifier(attribute_name):
        raise ValueError(
            f'Attribute name: {attribute_name!s} not a valid identifier')

      if attribute_name.startswith('_'):
        raise ValueError(
            f'Attribute name: {attribute_name!s} starts with underscore')

      if keyword.iskeyword(attribute_name):
        raise ValueError(
            f'Attribute name: {attribute_name!s} matches keyword')

      if attribute_name in defined_attribute_names:
        raise ValueError(
            f'Attribute name: {attribute_name!s} already defined')

      defined_attribute_names.add(attribute_name)

  @classmethod
  def CreateClass(cls, data_type_definition):
    """Creates a new structure values class.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Returns:
      class: structure values class.
    """
    cls._ValidateDataTypeDefinition(data_type_definition)

    class_definition = cls._CreateClassTemplate(data_type_definition)

    namespace = {
        '__builtins__' : {
            'object': builtins.object,
            'super': builtins.super},
        '__name__': f'{data_type_definition.name:s}'}

    if sys.version_info[0] >= 3:
      # pylint: disable=no-member
      namespace['__builtins__']['__build_class__'] = builtins.__build_class__

    exec(class_definition, namespace)  # pylint: disable=exec-used

    return namespace[data_type_definition.name]
