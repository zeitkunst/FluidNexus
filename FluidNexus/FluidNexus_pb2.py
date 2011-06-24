# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


DESCRIPTOR = descriptor.FileDescriptor(
  name='FluidNexus.proto',
  package='FluidNexus',
  serialized_pb='\n\x10\x46luidNexus.proto\x12\nFluidNexus\"(\n\x10\x46luidNexusHashes\x12\x14\n\x0cmessage_hash\x18\x01 \x03(\t\"\xe7\x02\n\x11\x46luidNexusMessage\x12\x15\n\rmessage_title\x18\x01 \x01(\t\x12\x17\n\x0fmessage_content\x18\x02 \x01(\t\x12\x19\n\x11message_timestamp\x18\x03 \x01(\x02\x12\x14\n\x0cmessage_hash\x18\x04 \x01(\t\x12\x16\n\x0emessage_source\x18\x05 \x01(\t\x12\x14\n\x0cmessage_mine\x18\x06 \x01(\x08\x12?\n\x0cmessage_type\x18\x07 \x01(\x0e\x32).FluidNexus.FluidNexusMessage.MessageType\x12\x1a\n\x12message_attachment\x18\x08 \x01(\x0c\x12,\n$message_attachment_original_filename\x18\t \x01(\t\"8\n\x0bMessageType\x12\x08\n\x04TEXT\x10\x00\x12\t\n\x05IMAGE\x10\x01\x12\t\n\x05\x41UDIO\x10\x02\x12\t\n\x05VIDEO\x10\x03\"D\n\x12\x46luidNexusMessages\x12.\n\x07message\x18\x01 \x03(\x0b\x32\x1d.FluidNexus.FluidNexusMessageB%\n\x19net.fluidnexus.FluidNexusB\x06ProtosH\x03')



_FLUIDNEXUSMESSAGE_MESSAGETYPE = descriptor.EnumDescriptor(
  name='MessageType',
  full_name='FluidNexus.FluidNexusMessage.MessageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='TEXT', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='IMAGE', index=1, number=1,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='AUDIO', index=2, number=2,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='VIDEO', index=3, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=378,
  serialized_end=434,
)


_FLUIDNEXUSHASHES = descriptor.Descriptor(
  name='FluidNexusHashes',
  full_name='FluidNexus.FluidNexusHashes',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='message_hash', full_name='FluidNexus.FluidNexusHashes.message_hash', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=32,
  serialized_end=72,
)


_FLUIDNEXUSMESSAGE = descriptor.Descriptor(
  name='FluidNexusMessage',
  full_name='FluidNexus.FluidNexusMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='message_title', full_name='FluidNexus.FluidNexusMessage.message_title', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message_content', full_name='FluidNexus.FluidNexusMessage.message_content', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message_timestamp', full_name='FluidNexus.FluidNexusMessage.message_timestamp', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message_hash', full_name='FluidNexus.FluidNexusMessage.message_hash', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message_source', full_name='FluidNexus.FluidNexusMessage.message_source', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message_mine', full_name='FluidNexus.FluidNexusMessage.message_mine', index=5,
      number=6, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message_type', full_name='FluidNexus.FluidNexusMessage.message_type', index=6,
      number=7, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message_attachment', full_name='FluidNexus.FluidNexusMessage.message_attachment', index=7,
      number=8, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value="",
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message_attachment_original_filename', full_name='FluidNexus.FluidNexusMessage.message_attachment_original_filename', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _FLUIDNEXUSMESSAGE_MESSAGETYPE,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=75,
  serialized_end=434,
)


_FLUIDNEXUSMESSAGES = descriptor.Descriptor(
  name='FluidNexusMessages',
  full_name='FluidNexus.FluidNexusMessages',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='message', full_name='FluidNexus.FluidNexusMessages.message', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=436,
  serialized_end=504,
)


_FLUIDNEXUSMESSAGE.fields_by_name['message_type'].enum_type = _FLUIDNEXUSMESSAGE_MESSAGETYPE
_FLUIDNEXUSMESSAGE_MESSAGETYPE.containing_type = _FLUIDNEXUSMESSAGE;
_FLUIDNEXUSMESSAGES.fields_by_name['message'].message_type = _FLUIDNEXUSMESSAGE

class FluidNexusHashes(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _FLUIDNEXUSHASHES
  
  # @@protoc_insertion_point(class_scope:FluidNexus.FluidNexusHashes)

class FluidNexusMessage(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _FLUIDNEXUSMESSAGE
  
  # @@protoc_insertion_point(class_scope:FluidNexus.FluidNexusMessage)

class FluidNexusMessages(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _FLUIDNEXUSMESSAGES
  
  # @@protoc_insertion_point(class_scope:FluidNexus.FluidNexusMessages)

# @@protoc_insertion_point(module_scope)
