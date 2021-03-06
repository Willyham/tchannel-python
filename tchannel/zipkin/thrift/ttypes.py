# Copyright (c) 2015 Uber Technologies, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

#
# Autogenerated by Thrift Compiler (0.9.2)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py:tornado,dynamic,utf8strings,new_style,slots
#

from thrift.Thrift import TType, TMessageType, TException, TApplicationException

from thrift.protocol.TBase import TBase, TExceptionBase


class AnnotationType(TBase):
  BOOL = 0
  BYTES = 1
  I16 = 2
  I32 = 3
  I64 = 4
  DOUBLE = 5
  STRING = 6

  _VALUES_TO_NAMES = {
    0: "BOOL",
    1: "BYTES",
    2: "I16",
    3: "I32",
    4: "I64",
    5: "DOUBLE",
    6: "STRING",
  }

  _NAMES_TO_VALUES = {
    "BOOL": 0,
    "BYTES": 1,
    "I16": 2,
    "I32": 3,
    "I64": 4,
    "DOUBLE": 5,
    "STRING": 6,
  }


class Endpoint(TBase):
  """
  Attributes:
   - ipv4
   - port
   - serviceName
  """

  __slots__ = [ 
    'ipv4',
    'port',
    'serviceName',
   ]

  thrift_spec = (
    None, # 0
    (1, TType.I32, 'ipv4', None, None, ), # 1
    (2, TType.I32, 'port', None, None, ), # 2
    (3, TType.STRING, 'serviceName', None, None, ), # 3
  )

  def __init__(self, ipv4=None, port=None, serviceName=None,):
    self.ipv4 = ipv4
    self.port = port
    self.serviceName = serviceName

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.ipv4)
    value = (value * 31) ^ hash(self.port)
    value = (value * 31) ^ hash(self.serviceName)
    return value


class Annotation(TBase):
  """
  Attributes:
   - timestamp
   - value
   - duration
  """

  __slots__ = [ 
    'timestamp',
    'value',
    'duration',
   ]

  thrift_spec = (
    None, # 0
    (1, TType.DOUBLE, 'timestamp', None, None, ), # 1
    (2, TType.STRING, 'value', None, None, ), # 2
    (3, TType.I32, 'duration', None, None, ), # 3
  )

  def __init__(self, timestamp=None, value=None, duration=None,):
    self.timestamp = timestamp
    self.value = value
    self.duration = duration

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.timestamp)
    value = (value * 31) ^ hash(self.value)
    value = (value * 31) ^ hash(self.duration)
    return value


class BinaryAnnotation(TBase):
  """
  Attributes:
   - key
   - stringValue
   - doubleValue
   - boolValue
   - bytesValue
   - intValue
   - annotationType
  """

  __slots__ = [ 
    'key',
    'stringValue',
    'doubleValue',
    'boolValue',
    'bytesValue',
    'intValue',
    'annotationType',
   ]

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'key', None, None, ), # 1
    (2, TType.STRING, 'stringValue', None, None, ), # 2
    (3, TType.DOUBLE, 'doubleValue', None, None, ), # 3
    (4, TType.BOOL, 'boolValue', None, None, ), # 4
    (5, TType.STRING, 'bytesValue', None, None, ), # 5
    (6, TType.I64, 'intValue', None, None, ), # 6
    (7, TType.I32, 'annotationType', None, None, ), # 7
  )

  def __init__(self, key=None, stringValue=None, doubleValue=None, boolValue=None, bytesValue=None, intValue=None, annotationType=None,):
    self.key = key
    self.stringValue = stringValue
    self.doubleValue = doubleValue
    self.boolValue = boolValue
    self.bytesValue = bytesValue
    self.intValue = intValue
    self.annotationType = annotationType

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.key)
    value = (value * 31) ^ hash(self.stringValue)
    value = (value * 31) ^ hash(self.doubleValue)
    value = (value * 31) ^ hash(self.boolValue)
    value = (value * 31) ^ hash(self.bytesValue)
    value = (value * 31) ^ hash(self.intValue)
    value = (value * 31) ^ hash(self.annotationType)
    return value


class Span(TBase):
  """
  Attributes:
   - traceId
   - host
   - name
   - id
   - parentId
   - annotations
   - binaryAnnotations
   - debug
  """

  __slots__ = [ 
    'traceId',
    'host',
    'name',
    'id',
    'parentId',
    'annotations',
    'binaryAnnotations',
    'debug',
   ]

  thrift_spec = (
    None, # 0
    (1, TType.STRING, 'traceId', None, None, ), # 1
    (2, TType.STRUCT, 'host', (Endpoint, Endpoint.thrift_spec), None, ), # 2
    (3, TType.STRING, 'name', None, None, ), # 3
    (4, TType.STRING, 'id', None, None, ), # 4
    (5, TType.STRING, 'parentId', None, None, ), # 5
    (6, TType.LIST, 'annotations', (TType.STRUCT,(Annotation, Annotation.thrift_spec)), None, ), # 6
    (7, TType.LIST, 'binaryAnnotations', (TType.STRUCT,(BinaryAnnotation, BinaryAnnotation.thrift_spec)), None, ), # 7
    (8, TType.BOOL, 'debug', None, False, ), # 8
  )

  def __init__(self, traceId=None, host=None, name=None, id=None, parentId=None, annotations=None, binaryAnnotations=None, debug=thrift_spec[8][4],):
    self.traceId = traceId
    self.host = host
    self.name = name
    self.id = id
    self.parentId = parentId
    self.annotations = annotations
    self.binaryAnnotations = binaryAnnotations
    self.debug = debug

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.traceId)
    value = (value * 31) ^ hash(self.host)
    value = (value * 31) ^ hash(self.name)
    value = (value * 31) ^ hash(self.id)
    value = (value * 31) ^ hash(self.parentId)
    value = (value * 31) ^ hash(self.annotations)
    value = (value * 31) ^ hash(self.binaryAnnotations)
    value = (value * 31) ^ hash(self.debug)
    return value


class Response(TBase):
  """
  Attributes:
   - ok
  """

  __slots__ = [ 
    'ok',
   ]

  thrift_spec = (
    None, # 0
    (1, TType.BOOL, 'ok', None, None, ), # 1
  )

  def __init__(self, ok=None,):
    self.ok = ok

  def __hash__(self):
    value = 17
    value = (value * 31) ^ hash(self.ok)
    return value

