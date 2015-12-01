from collections import namedtuple


class Node(namedtuple('Node', ['identifier', 'attrs'])):
    def __str__(self):
        return '\n'.join([self.identifier + ' ['] +
                         ['{attr} = {value}'.format(attr=attr, value=value)
                          for attr, value
                          in self.attrs.items()] +
                         [']'])

class Edge(namedtuple('Edge', ['head', 'tail', 'attrs'])):
    def __str__(self):
        return '\n'.join([self.head + ' -> ' + self.tail + ' ['] +
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
