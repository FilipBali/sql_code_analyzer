from queue import Queue


def get_next_node(visited_nodes: Queue,
                  ast_generator
                  ):
    """
    Get next AST node
    :param visited_nodes: Queue where are stored nodes which need to be visited as soon as possible
    :param ast_generator: Generator of AST
    :return:
    """
    if not visited_nodes.empty():
        nodes = visited_nodes.get()
        return nodes[0], nodes, False
    else:
        try:
            next_node = next(ast_generator)
            return next_node[0], next_node, False
        except (Exception,):
            return None, None, True


def skip_lower_nodes(visited_nodes,
                     ast_generator,
                     context_layer_node_depth):
    """
    Skip nodes with bigger depth when more details about this node are not needed
    :param visited_nodes: Queue where are stored nodes that need to be prioritised
    :param ast_generator: AST generator where nodes comes from
    :param context_layer_node_depth: Depth of current node
    :return: Nothing (The AST generator is shifted)
    """
    while 1:
        node, nodes, stop_parse = get_next_node(visited_nodes=visited_nodes,
                                                ast_generator=ast_generator)
        if node is None:
            break

        if context_layer_node_depth >= node.depth:
            visited_nodes.put(nodes)
            break
