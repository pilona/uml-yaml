#! /usr/bin/env python3

# TODO: Ellipsis or infinity?
# TODO: Handle nested classes?
# TODO: Enforce particular order in keys?
# TODO: Deal with circular references.
# TODO: type, stereotype

from textwrap import indent
from itertools import count
from functools import singledispatch

import dot


class Class:
    # TODO: Attributes or operations first?
    def __init__(self, identifier,
                 attributes=[], operations=[],
                 inherits=[], implements=[],
                 associations=[],
                 stereotype=None):
        self.identifier = identifier

        self.attributes = attributes
        self.operations = operations
        self.inherits = inherits
        self.associations = associations
        self.stereotype = stereotype

    def to_dot(self):
        if self.stereotype is not None:
            label = r'<<{}>>\n{}'.format(self.stereotype, self.identifier)
        else:
            label = self.identifier
        return dot.Node(self.identifier, {'label': label})


# Move to coroutine-based parser, and use .throw to abort? Or
# would generators and .throw be enough?

# http://code.activestate.com/recipes/52310-conditionals-in-expressions/

nodes = {}
# FIXME: Not thread-safe
nodes_seq = count()


@singledispatch
def parse_class(doc):
    raise NotImplementedError()

@parse_class.register(str)
def _(doc):
    assert doc not in nodes
    return Class(doc, stereotype='enumeration')


@parse_class.register(dict)
def _(doc):
    assert doc['class'] not in nodes

    return Class(doc['class'],
                 attributes=doc.get('attributes'),
                 operations=doc.get('operations'),
                 inherits=doc.get('inherits'),
                 implements=doc.get('implements'),
                 associations=doc.get('associations'),
                 stereotype=doc.get('stereotype'))


def parse_toplevel_map(doc):
    # Not just classes, but diagram attributes
    # TODO: package key
    if 'classes' in doc:
        yield from map(parse_class, doc['classes'])
    # Only class in diagram
    else:
        yield parse_class(doc)


def parse_toplevel_seq(doc):
    for node in doc:
        yield from parse_toplevel_map(node)


def parse_toplevel(doc):
    yield from {list: parse_toplevel_seq,
                dict: parse_toplevel_map,}[type(doc)](doc)


if __name__ == '__main__':
    from sys import stdin
    from tempfile import NamedTemporaryFile
    import subprocess

    import yaml

    try:
        yaml_loader = yaml.CLoader
    except:
        yaml_loader = yaml.Loader

    for doc in yaml.safe_load_all(stdin):
        print('---')
        print(doc)
        with NamedTemporaryFile(mode='x') as fp:
            print('digraph {', file=fp)
            print('node [ shape="rectangle" ]', file=fp)
            print('\n'.join(str(dottable.to_dot())
                            for dottable
                            in parse_toplevel(doc)),
                  file=fp)
            print('}', file=fp)
            fp.seek(0)
            tee = subprocess.Popen(['tee', '/dev/tty'], stdin=fp, stdout=subprocess.PIPE)
            subprocess.check_call(['dot', '-Txlib'], stdin=tee.stdout)
