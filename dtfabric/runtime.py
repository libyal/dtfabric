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

  _CLASS_TEMPLATE = u'\n'.join([
      u'class {type_name:s}(object):',
      u'  """{type_description:s}.',
      u'',
      u'  Attributes:',
      u'{class_attributes_description:s}',
      u'  """',
      u'',
      u'  def __init__(self, {init_arguments:s}):',
      u'    """Initializes an instance of {type_name:s}."""',
      u'    super({type_name:s}, self).__init__()',
      u'{instance_attributes:s}',
      u''])

  _PYTHON_NATIVE_TYPES = {
      definitions.TYPE_INDICATOR_BOOLEAN: u'bool',
      definitions.TYPE_INDICATOR_CHARACTER: u'str',
      definitions.TYPE_INDICATOR_FLOATING_POINT: u'float',
      definitions.TYPE_INDICATOR_INTEGER: u'int',
      definitions.TYPE_INDICATOR_UUID: u'uuid.UUID'}

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
    while type_description.endswith(u'.'):
      type_description = type_description[:-1]

    class_attributes_description = []
    init_arguments = []
    instance_attributes = []

    for member_definition in data_type_definition.members:
      attribute_name = member_definition.name

      description = member_definition.description or attribute_name
      while description.endswith(u'.'):
        description = description[:-1]

      member_data_type = getattr(member_definition, u'member_data_type', u'')
      if isinstance(member_definition, data_types.MemberDataTypeDefinition):
        member_definition = member_definition.member_data_type_definition

      member_type_indicator = member_definition.TYPE_INDICATOR
      if member_type_indicator == definitions.TYPE_INDICATOR_SEQUENCE:
        element_type_indicator = member_definition.element_data_type
        member_type_indicator = u'tuple[{0:s}]'.format(element_type_indicator)
      else:
        member_type_indicator = cls._PYTHON_NATIVE_TYPES.get(
            member_type_indicator, member_data_type)

      argument = u'{0:s}=None'.format(attribute_name)

      definition = u'    self.{0:s} = {0:s}'.format(attribute_name)

      description = u'    {0:s} ({1:s}): {2:s}.'.format(
          attribute_name, member_type_indicator, description)

      class_attributes_description.append(description)
      init_arguments.append(argument)
      instance_attributes.append(definition)

    class_attributes_description = u'\n'.join(
        sorted(class_attributes_description))
    init_arguments = u', '.join(init_arguments)
    instance_attributes = u'\n'.join(sorted(instance_attributes))

    template_values = {
        u'class_attributes_description': class_attributes_description,
        u'init_arguments': init_arguments,
        u'instance_attributes': instance_attributes,
        u'type_description': type_description,
        u'type_name': type_name}

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
    """Validates the data type defintion.

    Args:
      data_type_definition (DataTypeDefinition): data type definition.

    Raises:
      ValueError: if the data type definition is not considered valid.
    """
    if not cls._IsIdentifier(data_type_definition.name):
      raise ValueError(
          u'Data type definition name: {0!s} not a valid identifier'.format(
              data_type_definition.name))

    if keyword.iskeyword(data_type_definition.name):
      raise ValueError(
          u'Data type definition name: {0!s} matches keyword'.format(
              data_type_definition.name))

    members = getattr(data_type_definition, u'members', None)
    if not members:
      raise ValueError(
          u'Data type definition name: {0!s} missing members'.format(
              data_type_definition.name))

    defined_attribute_names = set()

    for member_definition in members:
      attribute_name = member_definition.name

      if not cls._IsIdentifier(attribute_name):
        raise ValueError(u'Attribute name: {0!s} not a valid identifier'.format(
            attribute_name))

      if attribute_name.startswith(u'_'):
        raise ValueError(u'Attribute name: {0!s} starts with underscore'.format(
            attribute_name))

      if keyword.iskeyword(attribute_name):
        raise ValueError(u'Attribute name: {0!s} matches keyword'.format(
            attribute_name))

      if attribute_name in defined_attribute_names:
        raise ValueError(u'Attribute name: {0!s} already defined'.format(
            attribute_name))

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
        u'__builtins__' : {
            u'object': builtins.object,
            u'super': builtins.super},
        u'__name__': u'{0:s}'.format(data_type_definition.name)}

    if sys.version_info[0] >= 3:
      namespace[u'__builtins__'][u'__build_class__'] = builtins.__build_class__

    exec(class_definition, namespace)  # pylint: disable=exec-used

    return namespace[data_type_definition.name]
