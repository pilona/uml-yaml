#! /usr/bin/env python3

# TODO: Ellipsis or infinity?
# TODO: Handle nested classes?
# TODO: Enforce particular order in keys?
# TODO: Deal with circular references.
# TODO: type, stereotype

from textwrap import indent
from itertools import count
from collections import ChainMap

import dot


class Class:
    # TODO: Attributes or operations first?
    def __init__(self, name,
                 attributes=[], operations=[],
                 inherits=[], implements=[],
                 associations=[],
                 stereotype=None):
        self.name = name

        self.attributes = attributes
        self.operations = operations
        self.inherits = inherits
        self.associations = associations
        self.stereotype = stereotype

    def to_dot(self):
        if self.stereotype is not None:
            identifier = self.stereotype + '_' + self.name
            label = r'<<{}>>\n{}'.format(self.stereotype, self.name)
        else:
            identifier = self.name
            label = self.name
        return dot.Node(identifier, {'label': label})

# Move to coroutine-based parser, and use .throw to abort? Or
# would generators and .throw be enough?

# http://code.activestate.com/recipes/52310-conditionals-in-expressions/

nodes = {}
# FIXME: Not thread-safe
nodes_seq = count()

def parse_class(doc, stereotype=None):
    if isinstance(doc, str):
        assert doc not in nodes
        yield Class(doc, stereotype=stereotype)
        return

    if stereotype is not None:
        assert 'stereotype' not in doc
    if 'class' in doc:
        name = doc['class']
    else:
        name = doc['name']
    assert name not in nodes

    yield Class(name,
                attributes=doc.get('attributes', []),
                operations=doc.get('operations', []),
                inherits=doc.get('inherits', []),
                implements=doc.get('implements', []),
                associations=doc.get('associations', []),
                stereotype=stereotype)


def parse_enum(doc):
    raise NotImplementedError()


def parse_map(doc):
    for box_type, box_parser in box_parsers.items():
        if box_type in doc:
            yield from box_parser(doc)
            return
    else:
        if 'type' in doc:
            if 'stereotype' in doc:
                kwargs = {stereotype: doc['stereotype']}
            else:
                kwargs = {}
            yield from box_parsers[doc['type']](doc, **kwargs)
            return
        else:
            raise NotImplementedError()


def parse_toplevel_map(doc):
    try:
        yield from parse_map(doc)
    # TODO: Cleaner way
    except NotImplementedError:
        for box_type, box_parser in box_parsers.items():
            pluralized = box_type + 's'
            print(pluralized)
            if pluralized in doc:
                yield from map(box_parser, doc[pluralized])
                return
        else:
            raise NotImplementedError()


def parse_toplevel_seq(doc):
    for node in doc:
        yield from parse_map(node)


def parse_toplevel(doc):
    yield from {list: parse_toplevel_seq,
                dict: parse_toplevel_map,}[type(doc)](doc)


stereotypes = {
    'abstract',
    # Enum or enumeration?
    'enum',
}

box_types = {
    'class': parse_class,
    'enum': parse_enum,
}

stereotyped_box_types = {
    stereotype + ' ' + 'class': \
      lambda box: parse_box(box, stereotype=stereotype)
    for stereotype in stereotypes
    for box_type, box_parser in box_types.items()
}

# TODO: Generalize to all types
box_parsers = ChainMap(
    box_types,
    stereotyped_box_types
)

plurals = {
    'class': 'classes',
    'enum': 'enums',
}

singulars = dict(map(reversed, plurals.items()))


if __name__ == '__main__':
    from sys import stdin

    import yaml

    try:
        yaml_loader = yaml.CLoader
    except:
        yaml_loader = yaml.Loader

    for doc in yaml.safe_load_all(stdin):
        print('---')
        print(doc)
        print('\n'.join(str(dottable.to_dot())
                        for dottable
                        in parse_toplevel(doc)))
