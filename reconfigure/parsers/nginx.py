from reconfigure.nodes import *
from reconfigure.parsers import BaseParser
import re


class NginxParser (BaseParser):
    """
    A parser for nginx configs
    """

    tokens = [
        (r"[\w_]+\s*?[^\n]*?{", lambda s, t: ('section_start', t)),
        (r'''("[^"]*"|'[^']*'|[\w_])+?[^;]+?((?:[^;"']|"[^"]*"|'[^']*')+)?;''', lambda s, t: ('option', t)),
        (r"\s", lambda s, t: 'whitespace'),
        (r"$^", lambda s, t: 'newline'),
        (r"\#.*?\n", lambda s, t: ('comment', t)),
        (r"\}", lambda s, t: 'section_end'),
    ]
    token_comment = '#'
    token_section_end = '}'

    """
    Strip unwanted characters like whitespace and semicolons from around val. Remove quotes when they surround a value.
    """
    def strip_value(self,val):
        val = val.strip('''\n \t;''')
        if (val[0] == val[-1]) and (val[0] == '"' or val[0] == "'") and (len(val) > 2):
            val = val[1:-1]
        return val

    def parse(self, content):
        scanner = re.Scanner(self.tokens, re.DOTALL)
        tokens, remainder = scanner.scan(' '.join(filter(None, content.split(' '))))
        if remainder:
            raise Exception('Invalid tokens: %s. Tokens: %s' % (remainder, tokens))

        node = RootNode()
        node.parameter = None
        node_stack = []
        next_comment = None

        while len(tokens) > 0:
            token = tokens[0]
            tokens = tokens[1:]
            if token in ['whitespace', 'newline']:
                continue
            if token == 'section_end':
                node = node_stack.pop()
            if token[0] == 'comment':
                if not next_comment:
                    next_comment = ''
                else:
                    next_comment += '\n'
                next_comment += token[1].strip('#/*').strip()
            if token[0] == 'option':
                if ' ' in token[1]:
                    k, v = [self.strip_value(p) for p in re.split("(\s|\\\".*?\\\"|'.*?')", token[1],1) if p.strip()]
                else:
                    k = self.strip_value(token[1])
                    v = True
                prop = PropertyNode(k, v)
                prop.comment = next_comment
                next_comment = None
                node.children.append(prop)
            if token[0] == 'section_start':
                line = token[1][:-1].strip().split(None, 1) + [None]
                section = Node(line[0])
                section.parameter = line[1]
                section.comment = next_comment
                next_comment = None
                node_stack += [node]
                node.children.append(section)
                node = section

        return node

    def stringify(self, tree):
        return ''.join(self.stringify_rec(node) for node in tree.children)

    def stringify_rec(self, node):
        if isinstance(node, PropertyNode):
            if node.name:
                s = '%s %s;\n' % (node.name, node.value)
            else:
                s = '%s;\n' % (node.value)
        elif isinstance(node, IncludeNode):
            s = 'include %s;\n' % (node.files)
        else:
            result = '\n%s %s {\n' % (node.name, node.parameter or '')
            for child in node.children:
                result += '\n'.join('\t' + x for x in self.stringify_rec(child).splitlines()) + '\n'
            result += self.token_section_end + '\n'
            s = result
        if node.comment:
            s = ''.join(self.token_comment + ' %s\n' % l for l in node.comment.splitlines()) + s
        return s
