#! /usr/bin/env python3

# TODO: Ellipsis or infinity?
# TODO: Handle nested classes?
# TODO: Enforce particular order in keys?

from textwrap import indent
from itertools import count

# Move to coroutine-based parser, and use .throw to abort? Or
# would generators and .throw be enough?

# http://code.activestate.com/recipes/52310-conditionals-in-expressions/

nodes = {}
# FIXME: Not thread-safe
nodes_seq = count()

def parse_class(doc, stereotype=None):
    if isinstance(doc, str):
        assert doc not in nodes

        yield ' '.join([doc, '['])
        if stereotype is not None:
            yield r'label = "<<{}>>\n{}"'.format(stereotype, doc)
        else:
            yield r'label = "{}"'.format(doc)
        return
    if stereotype is not None:
        assert 'stereotype' not in doc
    assert doc['class'] not in nodes

    yield ' '.join([doc['class'], '['])
    yield ']'


def parse_map(doc):
    for box_type, box_parser in box_types.items():
        # TODO: Handle non-string keys?
        if box_type in doc:
            yield from box_parser(doc)
            return
        else:
            for stereotype in stereotypes:
                if ' '.join([stereotype, box_type]) in doc:
                    yield from box_parser(doc, stereotype=stereotype)
                    return
            else:
                raise NotImplementedError()


def parse_toplevel_map(doc):
    yield from parse_map(doc)


def parse_toplevel_seq(doc):
    for node in doc:
        yield from parse_map(node)


def parse_toplevel(doc):
    yield 'digraph {'
    yield from {list: parse_toplevel_seq,
                dict: parse_toplevel_map,}[type(doc)](doc)
    yield '}'


box_types = {
    'class': parse_class,
}

stereotypes = {
    'abstract',
    'enum',
}


from sys import stdin

import yaml

try:
    yaml_loader = yaml.CLoader
except:
    yaml_loader = yaml.Loader

for doc in yaml.safe_load_all(stdin):
    print('---')
    print(doc)
    print('\n'.join(parse_toplevel(doc)))
