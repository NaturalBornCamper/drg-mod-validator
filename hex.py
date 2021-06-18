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
    def read_booleans(file, count=1):
        return struct.unpack(str(count) + 'h', file.read(count * 2))

    @staticmethod
    def read_ints(file, count=1):
        return struct.unpack(str(count) + 'i', file.read(count * 4))

    @staticmethod
    def read_floats(file, count=1):
        return [round(value, 3) for value in struct.unpack(str(count) + 'f', file.read(count * 4))]

    @staticmethod
    def read_single_bool(file):
        return PropertyReader.read_booleans(file, 1)[0]

    @staticmethod
    def read_single_int(file):
        return PropertyReader.read_ints(file, 1)[0]

    @staticmethod
    def read_single_float(file):
        return PropertyReader.read_floats(file, 1)[0]

    @staticmethod
    def BoolProperty(file, property):
        file.seek(property['Value Offset'])
        return PropertyReader.read_single_bool(file)

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
        # BoolProperty in ArrayProperty not tested, didn't see any ArrayProperty[BoolProperty] to test
        elif property['Tag Data']['Name'] == 'BoolProperty':
            file.seek(property['Value Offset'] + 4)
            return PropertyReader.read_booleans(file, property['Data Value']['Count'])
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
        'BoolProperty': BoolProperty.__func__,
        'IntProperty': IntProperty.__func__,
        'FloatProperty': FloatProperty.__func__,
        'TextProperty': TextProperty.__func__,
        'ArrayProperty': ArrayProperty.__func__,
        'StructProperty': StructProperty.__func__,
    }


class PropertyWriter:
    @staticmethod
    def write_booleans(file, values, count=1):
        file.write(struct.pack(str(count) + 'h', *values))

    @staticmethod
    def write_ints(file, values, count=1):
        file.write(struct.pack(str(count) + 'i', *values))

    @staticmethod
    def write_floats(file, values, count=1):
        file.write(struct.pack(str(count) + 'f', *values))

    @staticmethod
    def write_single_bool(file, value):
        PropertyWriter.write_booleans(file, [value])

    @staticmethod
    def write_single_int(file, value):
        PropertyWriter.write_ints(file, [value])

    @staticmethod
    def write_single_float(file, value):
        PropertyWriter.write_floats(file, [value])

    @staticmethod
    def BoolProperty(file, property, modded_value):
        file.seek(property['Value Offset'])
        PropertyWriter.write_single_bool(file, modded_value)
        return True

    @staticmethod
    def IntProperty(file, property, modded_value):
        file.seek(property['Value Offset'])
        PropertyWriter.write_single_int(file, modded_value)
        return True

    @staticmethod
    def FloatProperty(file, property, modded_value):
        file.seek(property['Value Offset'])
        PropertyWriter.write_single_float(file, modded_value)
        return True

    @staticmethod
    def TextProperty(file, property, modded_value):
        property_offset = property['Value Offset']
        property_size = property['Size']
        file.seek(property_offset)
        file.write(struct.pack(str(property_size) + 'c', *[i.encode('ISO-8859-1') for i in modded_value]))
        return True

    @staticmethod
    def ArrayProperty(file, property, modded_value):
        # If this property tag data is not supported, pass it
        if property['Tag Data']['Name'] == 'FloatProperty':
            file.seek(property['Value Offset'] + 4)
            PropertyWriter.write_floats(file, modded_value, property['Data Value']['Count'])
            return True
        elif property['Tag Data']['Name'] == 'IntProperty':
            file.seek(property['Value Offset'] + 4)
            PropertyWriter.write_ints(file, modded_value, property['Data Value']['Count'])
            return True
        # BoolProperty in ArrayProperty not tested, didn't see any ArrayProperty[BoolProperty] to test
        elif property['Tag Data']['Name'] == 'BoolProperty':
            file.seek(property['Value Offset'] + 4)
            PropertyWriter.write_booleans(file, modded_value, property['Data Value']['Count'])
            return True
        return False

    @staticmethod
    def StructProperty(file, property, modded_value):
        # If this property tag data is not supported, pass it
        if property['Tag Data']['Name'] == 'RandInterval':
            file.seek(property['Value Offset'] + StructProperty.RandInterval.OFFSET1)
            for x in modded_value:
                val = [PropertyWriter.write_single_float(file, x[0])]
                file.seek(StructProperty.RandInterval.OFFSET2, os.SEEK_CUR)
                val.append(PropertyWriter.write_single_int(file, x[1]))
                file.seek(StructProperty.RandInterval.OFFSET3, os.SEEK_CUR)
                val.append(PropertyWriter.write_single_int(file, x[2]))
                file.seek(StructProperty.RandInterval.OFFSET4, os.SEEK_CUR)
            return True
        return False

    methods = {
        'BoolProperty': BoolProperty.__func__,
        'IntProperty': IntProperty.__func__,
        'FloatProperty': FloatProperty.__func__,
        'TextProperty': TextProperty.__func__,
        'ArrayProperty': ArrayProperty.__func__,
        'StructProperty': StructProperty.__func__,
    }

# SUPPORTED_PROPERTY_TYPES = ["IntProperty", "FloatProperty", "TextProperty", "ArrayProperty", "StructProperty"]
# SUPPORTED_ARRAY_PROPERTY_TAG_DATA = ["FloatProperty", "RandInterval"]
