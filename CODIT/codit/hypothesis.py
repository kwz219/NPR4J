import copy

from codit.grammar import Grammar, DecodeTree, Rule


class Hypothesis:
    def __init__(self, arg):
        if isinstance(arg, Grammar):
            grammar = arg
            self.grammar = grammar
            root = grammar.root_node
            # assert isinstance(root, ASTNode)
            self.tree = DecodeTree(root.type, root.label, root.value, t=0)
            assert isinstance(self.tree, DecodeTree)
            self.frontier_stack = [self.tree]
            self.t = 0
            self.node_id = grammar.get_node_type_id(self.tree)
            self.parent_rule_id = -1
            self.current_rule_id = -1
            self.n_timestep = 0

        #
        # elif isinstance(arg, Hypothesis):
        #     self.grammar = arg.grammar
        #     """Copy the tree and the stack simultaeneously"""
        #     root = arg.tree
        #     self.frontier_stack = [None for node in arg.frontier_stack]
        #     self.tree = self.copy_tree(arg, root)
        #     self.t = arg.t
        #     self.score = arg.score
        #     self.decoder_state = copy.copy(arg.decoder_state)
        #     self.decoder_cell = copy.copy(arg.decoder_cell)
        #     self.hist_h = copy.copy(arg.hist_h)
        #     self.action_embed = copy.copy(arg.action_embed)
        #     self.node_id = arg.node_id
        #     self.parent_rule_id = arg.parent_rule_id
        #     self.current_rule_id = arg.current_rule_id
        #     self.n_timestep = arg.n_timestep
        #     self.log = arg.log
        #     self.lm_prev_state = arg.lm_prev_state
        #     self.lm_prev_word = arg.lm_prev_word

    def copy_tree(self, arg, root):
        assert isinstance(arg, Hypothesis)
        assert isinstance(root, DecodeTree)
        root_node = DecodeTree(root.type, root.label, root.value, t=root.t)
        if root in arg.frontier_stack:
            idx = arg.frontier_stack.index(root)
            self.frontier_stack[idx] = root_node
        new_children = []
        for child in root.children:
            new_child = self.copy_tree(arg, child)
            new_child.parent = root
            new_children.append(new_child)
        root_node.children = new_children
        return root_node

    def is_completed(self):
        return len(self.frontier_stack) == 0

    def frontier_node(self):
        if not self.is_completed():
            return self.frontier_stack[-1]
        else:
            return None

    def apply_rule(self, rule, rule_probability=1.0):
        assert isinstance(rule, Rule)
        parent = rule.parent
        # assert isinstance(parent, ASTNode)
        children = rule.children
        fnt = self.frontier_stack.pop() # This is the frontier node, this node should be expanded
        assert isinstance(fnt, DecodeTree)
        fnt.applied_rule = rule
        if fnt.type == parent.type:
            num_child = len(children)
            new_children = []
            for i in range(num_child):
                new_child = DecodeTree(children[i].type, children[i].label, children[i].value, t=self.t + 1)
                new_child.parent = fnt
                new_children.append(new_child)
            fnt.children = new_children
            for i in range(num_child):
                child = new_children[-1-i]
                if not self.grammar.is_value_node(child):
                    self.frontier_stack.append(child)

            # fnt = self.frontier_stack.pop()
            # while self.grammar.is_value_node(fnt):
            #     self.frontier_stack.pop()
            # self.frontier_stack.append(fnt)
        else :
            raise ValueError('Invalid Rule, Rule Head does not match with the frontier node!')
        # if config.per_action_score:
        #     self.score = ((self.score * self.t) + np.log2(rule_probability)) / (self.t + 1)
        # else:
        #     self.score = self.score + np.log2(rule_probability)
        self.t += 1
        self.parent_rule_id = self.current_rule_id

    def append_token(self, token, token_prob=1.0):
        # debug(self.frontier_stack)
        fnt = self.frontier_stack.pop()
        assert self.grammar.is_value_node(fnt)
        fnt.value = token
        # if config.per_action_score:
        #     self.score = ((self.score * self.t) + np.log2(token_prob)) / (self.t + 1)
        # else:
        #     self.score = self.score + np.log2(token_prob)
        self.t += 1

    def __repr__(self):
        try:
            frontier = self.frontier_node()
        except:
            frontier = 'Already Completed'
        # return 'Tree : ' + str(self.tree) + '\n' + 'Stack : ' + str(self.frontier_stack) + \
        #        '\nFrontier : ' + str(frontier) + '\n\n'
        return str(self.tree)

    def get_action_parent_t(self):
        try:
            frontier = self.frontier_node()
        except:
            frontier = None
        if frontier is not None:
            if frontier.parent is None:
                return -1
            else:
                return frontier.parent.t
        else:
            return 0

    def stack_equal(self, other):
        assert isinstance(other, Hypothesis)
        if len(self.frontier_stack) == len(other.frontier_stack):
            for a, b in zip(self.frontier_stack, other.frontier_stack):
                assert isinstance(a, DecodeTree) and isinstance(b, DecodeTree)
                if a.type != b.type or a.label != b.label or a.value != b.value:
                    return False
            return True
        else:
            return False

    def tree_equal(self, other):
        return self.tree.tree_equal(other.tree)

    def __eq__(self, other):
        return self.stack_equal(other) and self.tree_equal(other)

    def __hash__(self):
        return str(self.tree).__hash__()

    def get_terminal_sequence(self):
        if self.tree is None:
            return None
        return self.tree.get_leaf_typ_sequence()
        pass