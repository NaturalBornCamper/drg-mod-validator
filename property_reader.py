import os
import struct
from pprint import pprint


class StructProperty:
    class RandInterval:
        OFFSET1 = 111
        OFFSET2 = 78 - 4
        OFFSET3 = 29 - 4
        OFFSET4 = 45 - 4


class PropertyReader:

    @staticmethod
    def read_ints(file, count=1):
        return struct.unpack(str(count) + 'i', file.read(count * 4))

    @staticmethod
    def read_floats(file, count=1):
        return [round(value, 2) for value in struct.unpack(str(count) + 'f', file.read(count * 4))]

    @staticmethod
    def read_single_int(file):
        return PropertyReader.read_ints(file, 1)[0]

    @staticmethod
    def read_single_float(file):
        return PropertyReader.read_floats(file, 1)[0]

    @staticmethod
    def IntProperty(file, property):
        file.seek(property['Value Offset'])
        return PropertyReader.read_single_int(file)

    @staticmethod
    def FloatProperty(file, property):
        file.seek(property['Value Offset'])
        return PropertyReader.read_single_float(file)

    @staticmethod
    def TextProperty(file, property):
        property_offset = property['Value Offset']
        property_size = property['Size']
        file.seek(property_offset)
        text_bytes = struct.unpack(str(property_size) + 'c', file.read(property_size))
        return [i.decode('ISO-8859-1') for i in text_bytes]


    @staticmethod
    def ArrayProperty(file, property):
        # If this property tag data is not supported, pass it
        if property['Tag Data']['Name'] == 'FloatProperty':
            file.seek(property['Value Offset'] + 4)
            return PropertyReader.read_floats(file, property['Data Value']['Count'])
        elif property['Tag Data']['Name'] == 'IntProperty':
            file.seek(property['Value Offset'] + 4)
            return PropertyReader.read_ints(file, property['Data Value']['Count'])
        else:
            return False

    @staticmethod
    def StructProperty(file, property):
        # If this property tag data is not supported, pass it
        if property['Tag Data']['Name'] == 'RandInterval':
            file.seek(property['Value Offset'] + StructProperty.RandInterval.OFFSET1)
            values = []
            loop_count = int((property['Size'] - 94) / 152)
            for _ in range(0, loop_count):
                val = [PropertyReader.read_single_float(file)]
                file.seek(StructProperty.RandInterval.OFFSET2, os.SEEK_CUR)
                val.append(PropertyReader.read_single_int(file))
                file.seek(StructProperty.RandInterval.OFFSET3, os.SEEK_CUR)
                val.append(PropertyReader.read_single_int(file))
                file.seek(StructProperty.RandInterval.OFFSET4, os.SEEK_CUR)
                values.append(val)
            return values
        else:
            return False

    methods = {
        'IntProperty': IntProperty.__func__,
        'FloatProperty': FloatProperty.__func__,
        'TextProperty': TextProperty.__func__,
        'ArrayProperty': ArrayProperty.__func__,
        'StructProperty': StructProperty.__func__,
    }

# SUPPORTED_PROPERTY_TYPES = ["IntProperty", "FloatProperty", "TextProperty", "ArrayProperty", "StructProperty"]
# SUPPORTED_ARRAY_PROPERTY_TAG_DATA = ["FloatProperty", "RandInterval"]
