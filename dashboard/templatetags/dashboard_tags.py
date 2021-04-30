from django import template
register = template.Library()

@register.simple_tag
def get_carry(user):
    if user is not None:
        return dfs(set(),user,0)

def dfs(visited, node,total_amount):
    if node not in visited:
        print (node)
        if node is  None:
            return total_amount
        visited.add(node)
        left=dfs(visited, node.left,total_amount)
        right=dfs(visited, node.right,total_amount)
        total_amount=node.investment_carry

        return total_amount