import copy
import os
from typing import Union, Tuple, List

import tree_sitter
from tree_sitter import Language, Parser
from apted import APTED, Config


def get_ancestor_type_chains(
        node: tree_sitter.Node
) -> List[str]:
    types = [str(node.type)]
    while node.parent is not None:
        node = node.parent
        types.append(str(node.type))
    return types


class Node:
    def __init__(self):
        self.type = None
        self.value = ""
        self.children = []

    def print(self, level=0):
        for _ in range(level):
            print("\t", end="")
        print(self.type, self.value, sep=", ")
        for child in self.children:
            child.print(level+1)


class CustomConfig(Config):
    def rename(self, node1, node2):
        """Compares attribute .value of trees"""
        return 1 if (node1.value != node2.value or node1.type != node2.type) else 0

    def children(self, node):
        """Get left and right children of binary tree"""
        return node.children


def strip_identifiers_from_tree(
    code,
    complete_tree: tree_sitter.Node
):
    root = Node()
    root.type = complete_tree.type
    value_set = set()
    if len(complete_tree.children) == 0:
        try:
            value = code[complete_tree.start_byte:complete_tree.end_byte].decode()
        except:
            value = ""
        if 'identifier' in str(root.type) or 'literal' in str(root.type):
            root.value = ""
            value_set.add(value)
        else:
            root.value = value
    for child in complete_tree.children:
        child_value_set, child_node = strip_identifiers_from_tree(code, child)
        value_set = value_set.union(child_value_set)
        root.children.append(child_node)
    return value_set, root


class Tree:
    def __init__(
            self,
            parser_path: str,
            code: Union[str, bytes],
            language: str = "java",
    ):
        if not os.path.exists(parser_path):
            raise ValueError(
                f"Language parser does not exist at {parser_path}. Please run `setup.sh` to properly set the "
                f"environment!")
        self.lang_object = Language(parser_path, language)
        self.parser = Parser()
        self.parser.set_language(self.lang_object)
        code = code.strip()
        if not code.startswith("class"):
            code = "class A { \n" + code + "\n}"
        self.code = code
        self.complete_tree = self.parse_code(code.encode())
        self.identifier_list, self.stripped_tree = strip_identifiers_from_tree(code.encode(), self.complete_tree)
        pass

    def parse_code(
            self,
            code: bytes
    ) -> tree_sitter.Node:
        """
        This function parses a given code and return the root node.
        :param code:
        :return: tree_sitter.Node, the root node of the parsed tree.
        """
        tree = self.parser.parse(code)
        return tree.root_node

    def num_new_identifiers_introduced(
            self,
            new_tree
    ):
        return len(new_tree.identifier_list.difference(self.identifier_list))

    def stripped_tree_edit_distance(self, new_tree):
        apted = APTED(self.stripped_tree, new_tree.stripped_tree, CustomConfig())
        return apted.compute_edit_distance()


def compute_tree_distance(
        buggy_code,
        fixed_code,
        parser_path="parser/languages.so"
):
    buggy_tree = Tree(parser_path=parser_path, code=buggy_code)
    fixed_tree = Tree(parser_path=parser_path, code=fixed_code)
    return buggy_tree.stripped_tree_edit_distance(fixed_tree)


def number_of_new_identifiers_in_fixed_code(
        buggy_code,
        fixed_code,
        parser_path="parser/languages.so"
):
    buggy_tree = Tree(parser_path=parser_path, code=buggy_code)
    fixed_tree = Tree(parser_path=parser_path, code=fixed_code)
    return buggy_tree.num_new_identifiers_introduced(fixed_tree)


if __name__ == '__main__':
    buggy_code = """
    void foo(int n){
        for (int i = 0; i < n; i++){
            n = n + i;
        }
        return n;
    }
    """
    fixed_code = """
    void foo(int n){
        for (int i = 0; i < n; i++){
            n = n + j;
        }
        return n;
    }
    """
    print(
        compute_tree_distance(
            buggy_code=buggy_code,
            fixed_code=fixed_code,
            parser_path="parser/languages.so"
        )
    )

    print(
        number_of_new_identifiers_in_fixed_code(
            buggy_code=buggy_code,
            fixed_code=fixed_code,
            parser_path="parser/languages.so"
        )
    )

