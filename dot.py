from collections import namedtuple


class Node(namedtuple('Node', ['identifier', 'attrs'])):
    def __str__(self):
        return '\n'.join([self.identifier + ' ['] +
                         ['{attr} = {value}'.format(attr=attr, value=value)
                          for attr, value
                          in self.attrs.items()] +
                         [']'])

