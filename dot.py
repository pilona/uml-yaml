from collections import namedtuple


def _node_name(identifier):
    if identifier in {'node', 'edge'}:
        return identifier
    else:
        return '"' + identifier + '"'


class Node(namedtuple('Node', ['identifier', 'attrs'])):
    def __str__(self):
        return '\n'.join([_node_name(self.identifier) + ' ['] +
                         ['{attr} = {value}'.format(attr=attr, value=value)
                          for attr, value
                          in self.attrs.items()] +
                         [']'])

class Edge(namedtuple('Edge', ['head', 'tail', 'attrs'])):
    def __str__(self):
        return '\n'.join([_node_name(self.head) + ' -> ' + _node_name(self.tail) + ' ['] +
                         ['{attr} = "{value}"'.format(attr=attr, value=value)
                          for attr, value
                          in self.attrs.items()] +
                         [']'])


class Digraph(namedtuple('Digraph', ['nodes', 'edges', 'attrs'])):
    def __str__(self):
        return '\n'.join(['digraph {'] +
                         ['{attr} = "{value}"'.format(attr=attr, value=value)
                          for attr, value
                          in self.attrs.items()] +
                         [str(node) for node in self.nodes] +
                         [str(edge) for edge in self.edges] +
                         ['}'])
