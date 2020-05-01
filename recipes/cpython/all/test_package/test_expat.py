import xml.parsers.expat


# 3 handler functions
def start_element(name, attrs):
    print('Start element:', name, attrs)


def end_element(name):
    print('End element:', name)


def char_data(data):
    print('Character data:', repr(data))


p = xml.parsers.expat.ParserCreate()

p.StartElementHandler = start_element
p.EndElementHandler = end_element
p.CharacterDataHandler = char_data

p.Parse("""<?xml version="1.0"?>
<parent id="top"><child1 name="paul">Text goes here</child1>
<child2 name="fred">More text</child2>
</parent>""", 1)
