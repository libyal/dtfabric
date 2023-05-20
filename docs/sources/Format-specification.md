# Format specification

## Overview

Data types fabric (dtFabric) is a YAML-based definition language to specify
format and data types.

* storage data types, such as integers, characters, structures
* semantic data types, such as constants, enumerations
* layout data types, such as format, vectors, trees

## Data type definition

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
aliases | List of strings | No | List of alternative names for the data type
description | string | No | Description of the data type
name | string | Yes | Name of the data type
type | string | Yes | Definition type <br> See section: [Data type definition types](#data-type-definition-types)
urls | List of strings | No | List of URLS that contain more information about the data type

### Data type definition types

Identifier | Description
--- | ---
boolean | Boolean
character | Character
constant | Constant
enumeration | Enumeration
floating-point | Floating-point
format | Data format metadata <br> See section: [Data format](#data-format)
integer | Integer
padding | Alignment padding, only supported as a member definition of a structure data type
stream | Stream
string | String
structure | Structure
structure-family | **TODO: add description**
union | Union data type
uuid | UUID (or GUID)

**TODO: consider adding the following types**

Identifier | Description
--- | ---
bit-field | Bit field (or group of bits)
fixed-point | Fixed-point data type
reference | **TODO: add description**

## Storage data types

Storage data types are data types that represent stored (or serialized) values.
In addition to the [Data type definition attributes](#data-type-definition)
storage data types also define:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
attributes | mapping | No | Data type attributes <br> See section: [Storage data type definition attributes](#storage-data-type-definition-attributes)

### Storage data type definition attributes

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
byte_order | string | No | Byte-order of the data type <br> Valid options are: "big-endian", "little-endian", "native" <br> The default is native

---
**NOTE:** middle-endian is a valid byte-ordering but currently not supported.

---

### Fixed-size data types

In addition to the [Storage data type definition attributes](#storage-data-type-definition-attributes)
fixed-size data types also define the following attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
size | integer or string | No | size of data type in number of units or "native" if architecture dependent <br> The default is "native"
units | string | No | units of the size of the data type <br> The default is bytes

#### Boolean

A boolean is a data type to represent true-or-false values.

```yaml
name: bool32
aliases: [BOOL]
type: boolean
description: 32-bit boolean type
attributes:
  size: 4
  units: bytes
  false_value: 0
  true_value: 1
```

Boolean data type specfic attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
false_value | integer | No | Integer value that represents False <br> The default is 0
true_value | integer | No | Integer value that represents True <br> The default is not-set, which represent any value except for the false_value

Currently supported size attribute values are: 1, 2 and 4 bytes.

#### Character

A character is a data type to represent elements of textual strings.

```yaml
name: wchar16
aliases: [WCHAR]
type: character
description: 16-bit wide character type
attributes:
  size: 2
  units: bytes
```

Currently supported size attribute values are: 1, 2 and 4 bytes.

#### Fixed-point

A fixed-point is a data type to represent elements of fixed-point values.

**TODO: add example**

#### Floating-point

A floating-point is a data type to represent elements of floating-point values.

```yaml
name: float64
aliases: [double, DOUBLE]
type: floating-point
description: 64-bit double precision floating-point type
attributes:
  size: 8
  units: bytes
```

Currently supported size attribute values are: 4 and 8 bytes.

#### Integer

An integer is a data type to represent elements of integer values.

```yaml
name: int32le
aliases: [LONG, LONG32]
type: integer
description: 32-bit little-endian signed integer type
attributes:
  byte_order: little-endian
  format: signed
  size: 4
  units: bytes
```

Integer data type specfic attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
format | string | No | Signed or unsiged <br> The default is signed

Currently supported size attribute values are: 1, 2, 4 and 8 bytes.

#### UUID (or GUID)

An UUID (or GUID) is a data type to represent a Globally or Universal unique
identifier (GUID or UUID) data types.

```yaml
name: known_folder_identifier
type: uuid
description: Known folder identifier.
attributes:
  byte_order: little-endian
```

Currently supported size attribute values are: 16 bytes.

### Variable-sized data types

#### Sequence

A sequence is a data type to represent a sequence of individual elements such
as an array of integers.

```yaml
name: page_numbers
type: sequence
description: Array of 32-bit page numbers.
element_data_type: int32
number_of_elements: 32
```

Sequence data type specfic attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
element_data_type | string | Yes | Data type of sequence element
elements_data_size | integer or string | See note | Integer value or expression to determine the data size of the elements in the sequence
elements_terminator | integer | See note | element value that indicates the end-of-string
number_of_elements | integer or string | See note | Integer value or expression to determine the number of elements in the sequence

---
**NOTE:** At least one of the elements attributes: "elements_data_size",
"elements_terminator" or "number_of_elements" must be set. As of version
20200621 "elements_terminator" can be set in combination with
"elements_data_size" or "number_of_elements".

---

**TODO: describe expressions and the map context**

#### Stream

A stream is a data type to represent a continous sequence of elements such as
a byte stream.

```yaml
name: data
type: stream
element_data_type: byte
number_of_elements: data_size
```

Stream data type specfic attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
element_data_type | string | Yes | Data type of stream element
elements_data_size | integer or string | See note | Integer value or expression to determine the data size of the elements in the stream
elements_terminator | integer | See note | element value that indicates the end-of-string
number_of_elements | integer or string | See note | Integer value or expression to determine the number of elements in the stream

---
**NOTE:** At least one of the elements attributes: "elements_data_size",
"elements_terminator" or "number_of_elements" must be set. As of version
20200621 "elements_terminator" can be set in combination with
"elements_data_size" or "number_of_elements".

---

**TODO: describe expressions and the map context**

#### String

A string is a data type to represent a continous sequence of elements with a
known encoding such as an UTF-16 formatted string.

```yaml
name: utf16le_string_with_size
type: string
ecoding: utf-16-le
element_data_type: wchar16
elements_data_size: string_data_size
```

```yaml
name: utf16le_string_with_terminator
type: string
ecoding: utf-16-le
element_data_type: wchar16
elements_terminator: "\x00\x00"
```

String data type specfic attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
encoding | string | Yes | Encoding of the string
element_data_type | string | Yes | Data type of string element
elements_data_size | integer or string | See note | Integer value or expression to determine the data size of the elements in the string
elements_terminator | integer | See note | element value that indicates the end-of-string
number_of_elements | integer or string | See note | Integer value or expression to determine the number of elements in the string

---
**NOTE:** At least one of the elements attributes: "elements_data_size",
"elements_terminator" or "number_of_elements" must be set. As of version
20200621 "elements_terminator" can be set in combination with
"elements_data_size" or "number_of_elements".

---

**TODO: describe elements_data_size and number_of_elements expressions and the map context**

### Storage data types with members

In addition to the [Storage data type definition attributes](#storage-data-type-definition-attributes)
storage data types with member also define the following attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
members | list | Yes | List of member definitions <br> See section: [Member definition](#member-definition)

#### Member definition

A member definition supports the following attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
aliases | List of strings | No | List of alternative names for the member
condition | string | No | Condition under which the member is condisidered to be present
data_type | string | See note | Name of the data type definition of the member
description | string | No | Description of the member
name | string | See note | Name of the member
type | string | See note | Name of the definition type of the member <br> See section: [Data type definition types](#data-type-definition-types)
value | integer or string | See note | Supported value
values | List of integers or strings | See note | Supported values

---
**NOTE:** The name attribute: "name" must be set for storage data types with
members except for the Union type where it is optional.

---

---
**NOTE:** One of the type attributes: "data_type" or "type" must be set. The
following definition types cannot be directly defined as a member definition:
"constant", "enumeration", "format" and "structure".

---

**TODO: describe member definition not supporting attributes.**

---
**NOTE:** Both the value attributes: "value" and "values" are optional but only
one is supported at a time.

---

**TODO: describe conditions**

#### Structure

A structure is a data type to represent a composition of members of other
data types.

**TODO: add structure size hint?**

```yaml
name: point3d
aliases: [POINT]
type: structure
description: Point in 3 dimensional space.
attributes:
  byte_order: little-endian
members:
- name: x
  aliases: [XCOORD]
  data_type: int32
- name: y
  data_type: int32
- name: z
  data_type: int32
```

```yaml
name: sphere3d
type: structure
description: Sphere in 3 dimensional space.
members:
- name: number_of_triangles
  data_type: int32
- name: triangles
  type: sequence
  element_data_type: triangle3d
  number_of_elements: sphere3d.number_of_triangles
```

#### Padding

Padding is a member definition to represent (alignment) padding as a byte
stream.

```yaml
name: padding1
type: padding
alignment_size: 8
```

Padding data type specfic attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
alignment_size | integer | Yes | Alignment size

Currently supported alignment_size attribute values are: 2, 4, 8 and 16 bytes.

---
**NOTE:** The padding is currently considered as required in the data stream.

---

#### Union

**TODO: describe union**

## Semantic types

### Constant

A constant is a data type to provide meaning (semantic value) to a single
predefined value. The value of a constant is typically not stored in a byte
stream but used at compile time.

```yaml
name: maximum_number_of_back_traces
aliases: [AVRF_MAX_TRACES]
type: constant
description: Application verifier resource enumeration maximum number of back traces
urls: ['https://msdn.microsoft.com/en-us/library/bb432193(v=vs.85).aspx']
value: 13
```

Constant data type specfic attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
value | integer or string | Yes | Integer or string value that the constant represents

### Enumeration

An enumeration is a data type to provide meaning (semantic value) to one or more
predefined values.

```yaml
name: handle_trace_operation_types
aliases: [eHANDLE_TRACE_OPERATIONS]
type: enumeration
description: Application verifier resource enumeration handle trace operation types
urls: ['https://msdn.microsoft.com/en-us/library/bb432251(v=vs.85).aspx']
values:
- name: OperationDbUnused
  number: 0
  description: Unused
- name: OperationDbOPEN
  number: 1
  description: Open (create) handle operation
- name: OperationDbCLOSE
  number: 2
  description: Close handle operation
- name: OperationDbBADREF
  number: 3
  description: Invalid handle operation
```

Enumeration value attributes:

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
aliases | list of strings | No | List of alternative names for the enumeration
description | string | No | Description of the enumeration value
name | string | Yes | Name the enumeration value maps to
number | integer | Yes | Number the enumeration value maps to

**TODO: add description**

## Layout types

### Data format

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
attributes | mapping | No | Data type attributes <br> See section: [Data format attributes](#data-format-attributes)
description | string | No | Description of the format
layout | mapping | Yes | Format layout definition
metadata | mapping | No | Metadata
name | string | Yes | Name of the format
type | string | Yes | Definition type <br> See section: [Data type definition types](#data-type-definition-types)
urls | List of strings | No | List of URLS that contain more information about the format

Example:

```yaml
name: mdmp
type: format
description: Minidump file format
urls: ['https://docs.microsoft.com/en-us/windows/win32/debug/minidump-files']
metadata:
  authors: ['John Doe <john.doe@example.com>']
  year: 2022
attributes:
  byte_order: big-endian
layout:
- data_type: file_header
  offset: 0
```

#### Data format attributes

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
byte_order | string | No | Byte-order of the data type <br> Valid options are: "big-endian", "little-endian", "native" <br> The default is native

---
**NOTE:** middle-endian is a valid byte-ordering but currently not supported.

---

### Structure family

A structure family is a layout type to represent multiple generations
(versions) of the same structure.

```yaml
name: group_descriptor
type: structure-family
description: Group descriptor of Extended File System version 2, 3 and 4
base: group_descriptor_base
members:
- group_descriptor_ext2
- group_descriptor_ext4
```

The structure members defined in the base structure are exposed at runtime.

**TODO:** define behavior if a structure family member does not define a
structure member defined in the base structure.

### Structure group

A structure group is a layout type to represent a group structures that share
a common trait.

```yaml
name: bsm_token
type: structure-group
description: BSM token group
base: bsm_token_base
identifier: token_type
members:
- bsm_token_arg32
- bsm_token_arg64
```

The structure group members are required to define the identifier structure
member with its values specific to the group member.

Attribute name | Attribute type | Required | Description
--- | --- | --- | ---
base | string | Yes | Base data type. Note that this must be a structure data type.
default | string | None | Default data type as fallback if no corresponding member data type is defined. Note that this must be a structure data type.
identifier | string | Yes | Name of the member in the base (structure) data type that identified a (group) member.
members | list | Yes | List of (group) member data types. Note that these must be a structure data types.
