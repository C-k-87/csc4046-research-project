from typing import List

def separate_paren_groups(paren_string: str) -> List[str]:
    stack = []
    result = []
    temp_str = ''
    open_paren = '('
    close_paren = ')'

    for char in paren_string:
        if char != ' ' and char != open_paren and char != close_paren:
            temp_str += char
        elif char == open_paren:
            stack.append(temp_str)
            temp_str = ''
        elif char == close_paren:
            if stack:
                result.append(stack.pop() + temp_str)
            else:
                raise ValueError("Unmatched closing parenthesis")
        else:
            continue

    return result

print(separate_paren_groups('( ) (( )) (( )( ))'))
['', '', '', '', '', '']