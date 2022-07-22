#!/bin/bash

function setup_repo() {
    mkdir -p sitter-libs;
    git clone https://github.com/tree-sitter/tree-sitter-java sitter-libs/java;
    mkdir -p "parser";
    python3 create_tree_sitter_parser.py sitter-libs;
    rm -rf sitter-libs;
}


function install_deps() {
    pip install tree-sitter==0.19.0;
    pip install apted==1.0.3;
    # Please add the command if you add any package.
}

install_deps;
setup_repo;
