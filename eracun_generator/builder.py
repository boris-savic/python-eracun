from lxml import etree


def build_xml(data):
    if data.get('_ns'):
        tag = etree.Element(data['_name'], nsmap=data['_ns'])
    else:
        tag = etree.Element(data['_name'])

    for attr, val in data.get('_attrs', []):
        tag.attrib[attr] = val

    for child, child_data in data.items():
        if not child.startswith('_'):
            child_tag = build_xml(child_data)
            tag.append(child_tag)

    if data.get('_value', None) is not None:
        tag.text = data['_value']

    # Sort the child elements
    if '_sorting' in data:
        tag[:] = sorted(tag, key=lambda element: data['_sorting'].index(element.tag))

    return tag
