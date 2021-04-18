import struct


class PropertyReader:
    @staticmethod
    def IntProperty(file, offset, size):
        file.seek(offset)
        return struct.unpack('i', file.read(size))

    @staticmethod
    def FloatProperty(file, offset, size):
        file.seek(offset)
        return struct.unpack('f', file.read(size))

    @staticmethod
    def TextProperty(file, offset, size):
        file.seek(offset + 51)
        # return struct.unpack('c', file.read(1))
        size = size - 52
        return struct.unpack(str(size) + 'c', file.read(size))

    @staticmethod
    def ArrayProperty(file, offset, size, tag=None):
        return ''
        file.seek(offset)
        return struct.unpack('f', file.read(4))

    @staticmethod
    def StructProperty(file, offset, size, tag=None):
        return ''
        file.seek(offset)
        return struct.unpack('f', file.read(4))

    methods = {
        'IntProperty': IntProperty.__func__,
        'FloatProperty': FloatProperty.__func__,
        'TextProperty': TextProperty.__func__,
        'ArrayProperty': ArrayProperty.__func__,
        'StructProperty': StructProperty.__func__,
    }

# SUPPORTED_PROPERTY_TYPES = ["IntProperty", "FloatProperty", "TextProperty", "ArrayProperty", "StructProperty"]
# SUPPORTED_PROPERTY_TAG_DATA = ["FloatProperty", "RandInterval"]
