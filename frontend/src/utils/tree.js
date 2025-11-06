export function buildTree(nodes, parentId = null) {
  const tree = [];
  for (const node of nodes) {
    if (node.parent === parentId) {
      const children = buildTree(nodes, node.id);
      if (children.length) {
        node.children = children;
      }
      tree.push(node);
    }
  }
  return tree;
}
