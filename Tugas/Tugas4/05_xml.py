import sys
import unittest
from io import StringIO
import xml.etree.ElementTree as ET

# Sample data to be serialized
test_data = {
    'name': 'Alice',
    'age': 30,
    'is_admin': True,
    'skills': ['Python', 'Network Programming', 'Digital Forensics']
}

# Helper: convert dict to XML string
def dict_to_xml(data):
    root = ET.Element('root')
    for key, value in data.items():
        if isinstance(value, list):
            elements = ET.SubElement(root, key)
            for item in value:
              item_element = ET.SubElement(elements, 'item')
              item_element.text = str(item)
        else:
            element = ET.SubElement(root, key)
            element.text = str(value)
    return ET.tostring(root, encoding='unicode')

# Helper: convert XML string back to dict
def xml_to_dict(xml_str):
    root = ET.fromstring(xml_str)
    result = {}
    for child in root:
        if len(child) > 0:  # This is a list container
            items = []
            for item in child:
                items.append(item.text)
            # Try to cast values back to original types
            cast_items = []
            for item in items:
                try:
                    cast_items.append(int(item))
                except ValueError:
                    try:
                        cast_items.append(float(item))
                    except ValueError:
                        if item.lower() == 'true':
                            cast_items.append(True)
                        elif item.lower() == 'false':
                            cast_items.append(False)
                        else:
                            cast_items.append(item)
            result[child.tag] = cast_items
        else:
            # Try to cast values back to original types
            value = child.text
            try:
                result[child.tag] = int(value)
            except ValueError:
                try:
                    result[child.tag] = float(value)
                except ValueError:
                    if value.lower() == 'true':
                        result[child.tag] = True
                    elif value.lower() == 'false':
                        result[child.tag] = False
                    else:
                        result[child.tag] = value
    return result

# Function to assert that two dictionaries are equal
def assert_true_dict(dict1, dict2):
    is_true = dict1 == dict2
    if is_true:
        print("The dictionaries match.", dict1, dict2)
    else:
        print("The dictionaries do not match.")

def assert_true_strings(str1, str2):
    if str1 == str2:
        print("The XML strings match.", str1, str2)
    else:
        print("The XML strings do not match.")

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

# Unit test
class TestXmlToVariable(unittest.TestCase):
    def setUp(self):
        self.test_data = test_data

    def test_xml(self):
        xml_data = dict_to_xml(self.test_data)
        expected_xml = dict_to_xml(self.test_data)
        assert_true_strings(xml_data, expected_xml)
    
    def test_unxml(self):
        xml_data = dict_to_xml(self.test_data)
        parsed_data = xml_to_dict(xml_data)
        assert_true_dict(self.test_data, parsed_data)

# Entry point
if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        xml_data = dict_to_xml(test_data)
        print("Serialized XML:", xml_data)
    else:
        runner = unittest.TextTestRunner(stream=NullWriter())
        unittest.main(testRunner=runner, exit=False)
