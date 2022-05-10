import json
from io import StringIO
from collections import OrderedDict, defaultdict, Iterable


class Grammar(object):
    def __init__(self, rules):
        """
        instantiate a grammar with a set of production rules of type Rule
        """
        self.rules = rules
        self.rule_index = defaultdict(list)
        self.rule_to_id = OrderedDict()

        node_types = set()
        lhs_nodes = set()
        rhs_nodes = set()
        for rule in self.rules:
            self.rule_index[rule.parent].append(rule)

            # we also store all unique node types
            for node in rule.nodes:
                node_types.add(str(node.type))

            lhs_nodes.add(rule.parent)
            for child in rule.children:
                rhs_nodes.add(child.as_type_node)

        root_node = lhs_nodes - rhs_nodes
        # print root_node
        assert len(root_node) == 1
        self.root_node = next(iter(root_node))

        self.terminal_nodes = rhs_nodes - lhs_nodes
        self.terminal_types = set([n.type for n in self.terminal_nodes])

        self.node_type_to_id = OrderedDict()
        for i, type in enumerate(node_types, start=0):
            self.node_type_to_id[type] = i

        for gid, rule in enumerate(rules, start=0):
            self.rule_to_id[rule] = gid

        self.id_to_rule = OrderedDict((v, k) for (k, v) in self.rule_to_id.items())

        # debug('num. rules: %d', len(self.rules))
        # debug('num. types: %d', len(self.node_type_to_id))
        # debug('root: %s', self.root_node)
        # debug('terminals: %s', ', '.join(repr(n) for n in self.terminal_nodes))

    def __iter__(self):
        return self.rules.__iter__()

    def __len__(self):
        return len(self.rule)

    def __getitem__(self, lhs):
        key_node = ASTNode(lhs.type, None)  # Rules are indexed by types only
        if key_node in self.rule_index:
            return self.rule_index[key_node]
        else:
            KeyError('key=%s' % key_node)

    def get_node_type_id(self, node):
        if isinstance(node, ASTNode):
            type_repr = str(node.type)
            return self.node_type_to_id[type_repr]
        else:
            # assert isinstance(node, str)
            # it is a type
            type_repr = str(node)
            return self.node_type_to_id[type_repr]

    def is_terminal(self, node):
        return node.type in self.terminal_types

    def is_value_node(self, node):
        raise NotImplementedError

    def __repr__(self):
        return ''


class JavaGrammar(Grammar):
    def __init__(self, rules, value_node_rules = None):
        super(JavaGrammar, self).__init__(rules)
        self.value_node_rules = {}
        if value_node_rules is not None:
            for key in value_node_rules:
                self.value_node_rules[key] = list(set(value_node_rules[key]))

    def is_value_node(self, node):
        # print node
        # assert isinstance(node, ASTNode)
        return node.type in self.terminal_types


class ASTNode(object):
    def __init__(self, node_type, label=None, value=None, children=None):
        self.type = node_type
        self.label = label
        self.value = value

        if type(self) is not Rule:
            self.parent = None

        self.children = list()

        if children:
            if isinstance(children, Iterable):
                for child in children:
                    self.add_child(child)
            elif isinstance(children, ASTNode):
                self.add_child(children)
            else:
                raise AttributeError('Wrong type for child nodes')

        assert not (bool(children) and bool(value)), 'terminal node with a value cannot have children'

    @property
    def is_leaf(self):
        return len(self.children) == 0

    @property
    def is_preterminal(self):
        return len(self.children) == 1 and self.children[0].is_leaf

    @property
    def size(self):
        if self.is_leaf:
            return 1

        node_num = 1
        for child in self.children:
            node_num += child.size

        return node_num

    @property
    def nodes(self):
        """a generator that returns all the nodes"""

        yield self
        for child in self.children:
            for child_n in child.nodes:
                yield child_n

    @property
    def as_type_node(self):
        """return an ASTNode with type information only"""
        return ASTNode(self.type)

    def get_property_dict(self):
        pro_dict = {
            'type': self.type,
            'value': self.value,
            'children': []
        }
        for child in self.children:
            pro_dict['children'].append(child.get_property_dict())
        return pro_dict

    def __repr__(self):
        return json.dumps(self.get_property_dict())

    def representation(self):
        repr_str = ''
        # if not self.is_leaf:
        repr_str += '('
        repr_str += str(self.type)
        if self.label is not None:
            repr_str += '{%s}' % self.label
        if self.value is not None:
            repr_str += '{val=%s}' % self.value
        # if not self.is_leaf:
        for child in self.children:
            repr_str += ' ' + child.__repr__()
        repr_str += ')'
        return repr_str

    def __hash__(self):
        code = hash(self.type)
        if self.label is not None:
            code = code * 37 + hash(self.label)
        if self.value is not None:
            code = code * 37 + hash(self.value)
        for child in self.children:
            code = code * 37 + hash(child)

        return code

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if hash(self) != hash(other):
            return False

        if self.type != other.type:
            return False

        if self.label != other.label:
            return False

        if self.value != other.value:
            return False

        if len(self.children) != len(other.children):
            return False

        for i in range(len(self.children)):
            if self.children[i] != other.children[i]:
                return False

        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, child_type):
        return next(iter([c for c in self.children if c.type == child_type]))

    def __delitem__(self, child_type):
        tgt_child = [c for c in self.children if c.type == child_type]
        if tgt_child:
            assert len(tgt_child) == 1, 'unsafe deletion for more than one children'
            tgt_child = tgt_child[0]
            self.children.remove(tgt_child)
        else:
            raise KeyError

    def add_child(self, child):
        child.parent = self
        self.children.append(child)

    def get_child_id(self, child):
        for i, _child in enumerate(self.children):
            if child == _child:
                return i

        raise KeyError

    def pretty_print(self):
        sb = StringIO()
        new_line = False
        self.pretty_print_helper(sb, 0, new_line)
        return sb.getvalue()

    def pretty_print_helper(self, sb, depth, new_line=False):
        if new_line:
            sb.write('\n')
            for i in range(depth):
                sb.write('\t')

        # sb.write('(')
        sb.write(str(self.type))
        if self.label is not None:
            sb.write('{%s}' % self.label)

        if self.value is not None:
            sb.write('{val=%s}' % self.value)

        if len(self.children) == 0:
            # sb.write(')')
            return

        sb.write('\t')
        new_line = True
        for child in self.children:
            child.pretty_print_helper(sb, depth + 2, new_line)

        # sb.write('\n')
        for i in range(depth):
            sb.write('\t')
        # sb.write(')')

    def get_leaves(self):
        if self.is_leaf:
            return [self]

        leaves = []
        for child in self.children:
            leaves.extend(child.get_leaves())
        return leaves

    def get_leaf_typ_sequence(self):
        if self.is_leaf:
            return [self.type]

        leaves = []
        for child in self.children:
            leaves.extend(child.get_leaf_typ_sequence())
        return leaves

    def to_rule(self, include_value=False):
        """
        transform the current AST node to a production rule
        """
        rule = Rule(self.type)
        for c in self.children:
            val = c.value if include_value else None
            child = ASTNode(c.type, c.label, val)
            rule.add_child(child)

        return rule

    def get_productions(self, include_value_node=False):
        """
        get the depth-first, left-to-right sequence of rule applications
        returns a list of production rules and a map to their parent rules
        attention: node value is not included in child nodes
        """
        rule_list = list()
        rule_parents = OrderedDict()
        node_rule_map = dict()
        s = list()
        s.append(self)
        rule_num = 0
        value_node_rules = {}

        while len(s) > 0:
            node = s.pop()
            for child in reversed(node.children):
                if not child.is_leaf:
                    s.append(child)
                elif include_value_node:
                    if child.value is not None:
                        s.append(child)
                if child.value is not None:
                    possible_values = []
                    if child.type in value_node_rules.keys():
                        possible_values = value_node_rules[child.type]
                    possible_values.append(child.value)
                    value_node_rules[child.type] = possible_values

            # only non-terminals and terminal nodes holding values
            # can form a production rule
            if node.children or node.value is not None:
                rule = Rule(node.type)
                if include_value_node:
                    rule.value = node.value

                for c in node.children:
                    val = None
                    child = ASTNode(c.type, c.label, val)
                    rule.add_child(child)

                rule_list.append(rule)
                if node.parent:
                    child_id = node.parent.get_child_id(node)
                    parent_rule = node_rule_map[node.parent]
                    rule_parents[(rule_num, rule)] = (parent_rule, child_id)
                else:
                    rule_parents[(rule_num, rule)] = (None, -1)
                rule_num += 1

                node_rule_map[node] = rule
        return rule_list, rule_parents, value_node_rules

    def copy(self):
        new_tree = ASTNode(self.type, self.label, self.value)
        if self.is_leaf:
            return new_tree

        for child in self.children:
            new_tree.add_child(child.copy())

        return new_tree


class DecodeTree(ASTNode):
    def __init__(self, node_type, label=None, value=None, children=None, t=-1):
        super(DecodeTree, self).__init__(node_type, label, value, children)
        self.t = t
        self.applied_rule = None

    def copy(self):
        new_tree = DecodeTree(self.type, self.label, value=self.value, t=self.t)
        new_tree.applied_rule = self.applied_rule
        if self.is_leaf:
            return new_tree

        for child in self.children:
            new_tree.add_child(child.copy())

        return new_tree

    def __eq__(self, other):
        return id(self) == id(other)

    def tree_equal(self, other):
        assert isinstance(other, DecodeTree)
        if (self.type != other.type) or (self.value != other.value) or (self.label != other.label):
            return False
        if len(self.children) != len(other.children):
            return False
        for a, b in zip(self.children, other.children):
            if not a.tree_equal(b):
                return False
        return True


    def __repr__(self):
        repr_str = ''
        repr_str += '('
        repr_str += str(self.type)
        if self.label is not None:
            repr_str += '{%s}' % self.label
        if self.value is not None:
            repr_str += '{val=%s}' % self.value
        for child in self.children:
            repr_str += ' ' + child.__repr__()
        repr_str += ')'
        return repr_str


class Rule(ASTNode):
    def __init__(self, *args, **kwargs):
        super(Rule, self).__init__(*args, **kwargs)

        assert self.value is None and self.label is None, 'Rule LHS cannot have values or labels'

    @property
    def parent(self):
        return self.as_type_node

    def __repr__(self):
        parent = str(self.type)

        if self.label is not None:
            parent += '{%s}' % self.label

        if self.value is not None:
            parent += '{val=%s}' % self.value

        return '%s -> %s' % (parent, ', '.join([repr(c) for c in self.children]))


def get_grammar(parse_trees):
    rules = set()
    # rule_num_dist = defaultdict(int)
    value_node_rules = {}
    for idx, parse_tree in enumerate(parse_trees):
        if idx % 1000 == 0:
            print(idx, len(parse_trees))
        parse_tree_rules, rule_parents, value_nodes = parse_tree.get_productions()
        for rule in parse_tree_rules:
            rules.add(rule)
        for node in value_nodes.keys():
            values = value_nodes[node]
            if node in value_node_rules.keys():
                values.extend(value_node_rules[node])
            value_node_rules[node] = values

    rules = list(sorted(rules, key=lambda x: x.__repr__()))
    grammar = JavaGrammar(rules, value_node_rules)
    return grammar
