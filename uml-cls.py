#! /usr/bin/env python3

# TODO: Ellipsis or infinity?
# TODO: Handle nested classes?
# TODO: Enforce particular order in keys?
# TODO: Deal with circular references.
# TODO: type, stereotype

from collections import namedtuple
from itertools import count
from functools import singledispatch
from textwrap import indent
from enum import Enum
from copy import deepcopy

import dot


AssociationType = Enum('AssociationType',
                       ['Aggregation',
                        'Association',
                        'Composition',
                        'Dependency',
                        'Generalization',
                        'InterfaceRealization',
                        'Realization'])


AssociationEnd = namedtuple('AssociationEnd', ['end', 'multiplicity', 'role'])

class Association:
    # By convention, the head is the target. So in a realization,
    # the head is the interface being realized.
    _association_type_map = {
        AssociationType.Aggregation: {
            'dir': 'both',
            'arrowhead': 'diamond',
            'arrowtail': 'none',
            'fillcolor': 'white',
            'style': 'solid',
        },
        AssociationType.Association: {
            'dir': 'both',
            'arrowhead': 'none',
            'arrowtail': 'normal',
            'style': 'solid',
        },
        AssociationType.Composition: {
            'arrowhead': 'diamond',
            'arrowtail': 'none',
            'fillcolor': 'black',
            'style': 'solid',
        },
        AssociationType.Dependency: {},
        AssociationType.Generalization: {
            'dir': 'both',
            'arrowhead': 'none',
            'arrowtail': 'normal',
            'fillcolor': 'white',
            'style': 'solid',
        },
        # Diff between realization and interface realization
        AssociationType.InterfaceRealization: {},
        AssociationType.Realization: {
            'dir': 'both',
            'arrowhead': 'none',
            'arrowtail': 'normal',
            'fillcolor': 'white',
            'style': 'dashed',
        },
    }

    def __init__(self,
                 head, tail,
                 association_type, association_class=None):
        self.head = head
        self.tail = tail
        self.association_type = association_type
        self.association_class = association_class

    def to_dot(self):
        attrs = deepcopy(type(self)._association_type_map[self.association_type])
        assert not self.head.role or not self.head.multiplicity
        assert not self.tail.role or not self.tail.multiplicity
        if self.head.role:
            attrs['headlabel'] = self.head.role
        elif self.head.multiplicity:
            attrs['headlabel'] = self.head.multiplicity
        if self.tail.role:
            attrs['taillabel'] = self.tail.role
        elif self.tail.multiplicity:
            attrs['taillabel'] = self.tail.multiplicity
        yield dot.Edge(head='type_' + self.head.end,
                       tail='type_' + self.tail.end,
                       attrs=attrs)


class Class:
    # TODO: Attributes or operations first?
    def __init__(self, identifier,
                 attributes=None, operations=None,
                 inherits=None, implements=None,
                 associations=None,
                 stereotype=None):
        self.identifier = identifier

        self.attributes = attributes or []
        self.operations = operations or []
        # TODO: Properly parse different forms
        self.inherits = []
        if inherits is not None:
            self.inherits = [inherits]
        self.associations = associations or []
        self.stereotype = stereotype

    def to_dot(self):
        identity = lambda s: s

        def element(name, **kwargs):
            def attributes(**kwargs2):
                return ' '.join('{}="{}"'.format(k, v)
                                for k, v
                                in kwargs2.items())
            def surrounder(s, **kwargs2):
                return '<{0}{2}>{1}</{0}>'.format(name,
                                                  s,
                                                  ' ' +  attributes(**kwargs, **kwargs2) if kwargs or kwargs2 else '')
            return surrounder

        table = element('table', cellborder=0)
        tr = element('tr')
        center = element('td', align='center')
        left = element('td', align='left')
        u = element('u')

        row = lambda s: tr(s) if s else ''
        cat = lambda *l: ''.join(l)
        lcat = lambda l: ''.join(l)

        stereotype = lambda s: center(r'<<{}>>'.format(s)) if s else ''
        identifier = identity
        operations = lambda operations: maybe(identity,
                                              identity,
                                              lcat(tr(left(operation(m))) for m in operations))
        attributes = lambda attributes: maybe(identity,
                                              identity,
                                              lcat(tr(left(attribute(m))) for m in attributes))

        private = lambda s: '- ' + s
        protected = lambda s: '# ' + s
        public = lambda s: '+ ' + s

        static = lambda s: s.join(['<u>', '</u>'])

        maybe = lambda p, f, s: f(s) if p else s

        append = lambda suffix: lambda s: s + suffix if s else s
        typed = lambda a, s: maybe(a.get('type'),
                                   lambda s: ': '.join([s, a['type']]),
                                   s)

        scoped = lambda a, s: maybe(a.get('scope'),
                                    lambda s: {'static': static}[a['scope']](s),
                                    s)
        visible = lambda a, s: maybe(a.get('visibility'),
                                     {'private': private,
                                      'protected': protected,
                                      'public': public,
                                      None: identity}[a.get('visibility')],
                                     s)
        attribute = lambda a: visible(a,
                                      scoped(a,
                                             typed(a, a['name'])))
        operation = lambda o: visible(o,
                                      scoped(o,
                                             typed(o,
                                                   parameterized(o, o['name']))))
        parentheses = '(', ')'
        braces = '{', '}'
        html = lambda *args: cat(*args).join(['<', '>'])
        parenthesized = lambda s: s.join(parentheses)
        braced = lambda s: s.join(braces)
        parameterized = lambda o, s: s + parenthesized(', '.join(
                                                           typed(p, p['name'])
                                                           for p
                                                           in o['parameters']))
        label = html(
                    table(
                        '<hr />'.join(
                            filter(
                                bool,
                                [tr(center(stereotype(self.stereotype)
                                           + identifier(self.identifier))),
                                 operations(self.operations),
                                 attributes(self.attributes)]))))
        yield dot.Node('type_' + self.identifier, {'label': label})
        for superclass in self.inherits:
            yield from Association(head=AssociationEnd(superclass, None, None),
                                   tail=AssociationEnd(self.identifier, None, None),
                                   association_type=AssociationType.Generalization).to_dot()
        for association in self.associations:
            head = association['head']
            tail = association.get('tail', {})
            yield from Association(head=AssociationEnd(head['name'],
                                                       head.get('multiplicity'),
                                                       head.get('role')),
                                   tail=AssociationEnd(self.identifier,
                                                       tail.get('multiplicity'),
                                                       tail.get('role')),
                                   association_type=AssociationType.__members__[association['type'].title()]).to_dot()


# TODO? Move to coroutine-based parser, and use .throw to abort? Or would
# generators and .throw be enough?

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
            print('node [ shape="none"; margin="0"; fontname="monospace" ]', file=fp)
            print('\n'.join(str(strrable)
                            for dottable in parse_toplevel(doc)
                            for strrable in dottable.to_dot()),
                  file=fp)
            print('}', file=fp)
            fp.seek(0)
            tee = subprocess.Popen(['tee', '/dev/tty'], stdin=fp, stdout=subprocess.PIPE)
            subprocess.check_call(['dot', '-Txlib'], stdin=tee.stdout)
