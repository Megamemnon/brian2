import enum
import sys
import types
import copy

Tokens = []
serial = 0
Transformations = []


class Environment:
    def __init__(self):
        self.debug = False
        self.debugindent = 0


class TokenType(enum.Enum):
    parenopen = 1
    parenclose = 2
    constant = 3
    number = 4
    quoted_text = 5
    unknown = 6


class DataNode:
    def __init__(self, type, symbol, val):
        self.type = type
        self.symbol = symbol
        self.val = val

    def getValue(self):
        if self.type == TokenType.number:
            return self.val
        return self.symbol


class TreeNode:
    def __init__(self, id):
        self.data = None  # .data may be another TreeNode or a DataNode
        self.next = None
        self.id = id

    def getFormula(self):
        formula = ""
        if type(self.data) is TreeNode:
            formula += "(" + self.data.getFormula() + ")"
        elif type(self.data) is DataNode:
            if self.data.type == TokenType.quoted_text:
                formula += '"' + self.data.symbol + '" '
            else:
                formula += self.data.symbol + " "
        else:
            pass
        if self.next is not None:
            formula += self.next.getFormula()
        return formula

    def getValue(self):
        if type(self.data) is DataNode:
            return self.data.getValue()
        return None

    def getValueList(self):
        values = []
        node = self.next
        while node:
            x = node.getValue()
            if type(x) is list:
                values.extend(x)
            else:
                values.append(x)
            node = node.next
        return values

    def equivalent(self, node):
        d = True
        n = True
        if type(node.data) is DataNode:
            if node.data.type == TokenType.constant and node.data.symbol[0].isupper():
                return True
            if type(self.data) is DataNode:
                if node.data.type != self.data.type:
                    return False
                if node.data.symbol != self.data.symbol:
                    return False
            else:
                return False
        else:
            if type(self.data) is DataNode:
                return False
            d = self.data.equivalent(node.data)
        if self.next:
            if node.next:
                n = self.next.equivalent(node.next)
            else:
                return False
        return d and n

    def unify(self, node):
        global serial
        d = []
        n = []
        if type(node.data) is DataNode:
            if node.data.type == TokenType.constant and node.data.symbol[0].isupper():
                if type(self.data) is TreeNode:
                    return [(node, self)]
                else:
                    s = TreeNode(serial)
                    serial += 1
                    s.data = copy.copy(self.data)
                    d = [(node, s)]
            elif type(self.data) is DataNode:
                if (
                    self.data.type != node.data.type
                    or self.data.symbol != node.data.symbol
                ):
                    return None
            else:
                return None
        else:
            if type(self.data) is TreeNode:
                d = self.data.unify(node.data)
        if self.next:
            if node.next:
                n = self.next.unify(node.next)
            else:
                return None
        if d is None and n is None:
            return None
        u = []
        if type(d) is list:
            u.extend(d)
        if type(n) is list:
            u.extend(n)
        return u

    def resolve(self, node):
        resolution = []
        if self.equivalent(node):
            u = self.unify(node)
            if u is not None:
                resolution.append([self, u])
        if type(self.data) is TreeNode:
            u = self.data.resolve(node)
            if u is not None:
                resolution.extend(u)
        if self.next:
            if node.next:
                u = self.next.resolve(node)
                if u is not None:
                    resolution.extend(u)
        if resolution == []:
            return None
        return resolution

    def replaceVariable(self, var, newnode):
        if type(self.data) is DataNode:
            if self.data.symbol == var:
                if type(newnode.data) is DataNode:
                    self.data = copy.copy(newnode.data)
                else:
                    self.data = copy.deepcopy(newnode)
        else:
            self.data.replaceVariable(var, newnode)
        if self.next:
            self.next.replaceVariable(var, newnode)

    def applyUnifier(self, unifier):
        if type(unifier) is list:
            for u in unifier:
                if type(self.data) is DataNode:
                    if self.data.symbol == u[0].data.symbol:
                        self.data = copy.deepcopy(u[1])
                    else:
                        self.replaceVariable(u[0].data.symbol, u[1])
                else:
                    self.replaceVariable(u[0].data.symbol, u[1])
        else:
            if type(self.data) is DataNode:
                if self.data.symbol == unifier[0].data.symbol:
                    self.data = copy.deepcopy(unifier[1])
                else:
                    self.replaceVariable(unifier[0].data.symbol, unifier[1])
            else:
                self.replaceVariable(unifier[0].data.symbol, unifier[1])

    def replaceNode(self, currentnode, newnode):
        if type(self.data) is TreeNode:
            if self.data.id == currentnode.id:
                self.data = newnode
            else:
                self.data.replaceNode(currentnode, newnode)
        if self.next:
            if self.next.id == currentnode.id:
                self.next = newnode
            else:
                self.next.replaceNode(currentnode, newnode)


def tokenize(formula):
    index = 0
    tokens = []
    while index < len(formula):
        c = formula[index]
        nc = 0
        if index + 1 < len(formula):
            nc = formula[index + 1]
        if c in "(":
            token = DataNode(TokenType.parenopen, "(", 0)
            tokens.append(token)
        elif c in ")":
            token = DataNode(TokenType.parenclose, ")", 0)
            tokens.append(token)
        elif c == '"':
            word = ""
            c = 0
            while index < len(formula) and c != '"':
                index += 1
                c = formula[index]
                word += c
            word = word[:-1]
            token = DataNode(TokenType.quoted_text, word, 0)
            tokens.append(token)
        elif c not in " \t\n\r,()":
            word = c
            while index < len(formula) and c not in " \t\n\r,()":
                index += 1
                c = formula[index]
                word += c
            word = word[:-1]
            index -= 1
            token = DataNode(TokenType.constant, word, 0)
            tokens.append(token)
        index += 1
    for token in tokens:
        if token.type == TokenType.constant:
            try:
                if str(int(token.symbol)) == token.symbol:
                    token.val = int(token.symbol)
                    token.type = TokenType.number
            except:
                pass
        if token.type == TokenType.constant:
            try:
                if str(float(token.symbol)) == token.symbol:
                    token.val = float(token.symbol)
                    token.type = TokenType.number
            except:
                pass
    return tokens


def parse(tokens):
    global Tokens, serial
    Tokens = tokens
    x = buildTree(0)
    return x[0]


def buildTree(tokenIndex):
    global Tokens, serial
    head = None
    tail = None
    node = None
    while tokenIndex < len(Tokens):
        token = Tokens[tokenIndex]
        match token.type:
            case TokenType.parenclose:
                return [head, tokenIndex + 1]
            case TokenType.parenopen:
                node = TreeNode(serial)
                serial += 1
                tokenIndex += 1
                x = buildTree(tokenIndex)
                node.data = x[0]
                tokenIndex = x[1] - 1
            case _:
                data = DataNode(token.type, token.symbol, token.val)
                node = TreeNode(serial)
                serial += 1
                node.data = data
        if node is not None:
            if head is None:
                head = node
                tail = node
            else:
                tail.next = node
                tail = tail.next
        tokenIndex += 1
    return [head, tokenIndex + 1]


def loadFile(filepath):
    prog = []
    with open(filepath, "r") as f:
        buffer = f.readlines()
    for b in buffer:
        line = b
        if b[-1] == "\n":
            line = b[:-1]
        l = line.split()
        if len(l) > 0:
            if l[0][0] != "#":
                prog.append(line)
    return prog


def apply(func, params):
    if type(func) is types.FunctionType:
        return func(params)
    elif type(func) is str:
        if func in ParamFunctions:
            return ParamFunctions[func](params)
        else:
            return [f'({func} {" ".join(params[0])})', TokenType.quoted_text]
    elif type(func) is list:
        for f in func:
            params = apply(f, params)
        return params
    return None


def eval(node, env):
    if node is None:
        return None
    if type(node.data) is DataNode:
        if node.data.symbol in PreFunctions:
            func = PreFunctions[node.data.symbol]
            node = func(node, env)
            if node is None:
                return None
    env2 = copy.copy(env)
    dbug = " "
    if env.debug:
        print(f"# {dbug:<{env.debugindent*2}}NODE: {node.getFormula()}")
        env2.debugindent += 1
    if type(node.data) is TreeNode:
        node.data = eval(node.data, env2)
    node.next = eval(node.next, env2)
    if type(node.data) is DataNode:
        if node.data.symbol in ParamFunctions:
            if env.debug:
                print(f"# {dbug:<{env.debugindent*2}}OPERATOR: {node.data.symbol}")
            params = node.getValueList()
            if env.debug:
                print(f"# {dbug:<{env.debugindent*2}}OPERAND: {params}")
            func = ParamFunctions[node.data.symbol]
            x = apply(func, [params, TokenType.unknown])
            if env.debug:
                print(f"# {dbug:<{env.debugindent*2}}RESULT: {x}")
            if x is None:
                return x
            else:
                match x[1]:
                    case TokenType.number:
                        return DataNode(x[1], str(x[0]), x[0])
                    case TokenType.constant | TokenType.quoted_text:
                        return DataNode(x[1], x[0], 0)
        return node


def runProgram(program):
    global Transformations
    env = Environment()
    i = 0
    while i < len(program):
        line = program[i]
        llist = line.split()
        while llist[-1] == "-":
            line = " ".join(llist[:-1])
            i += 1
            line += " " + program[i]
            llist = line.split()
        t = tokenize(line)
        p = parse(t)
        if p is not None:
            changed = True
            while changed:
                changed = False
                for t in Transformations:
                    l = t.data
                    r = t.next.data
                    res = p.resolve(l)
                    if res is not None:
                        for nu in res:
                            rc = copy.deepcopy(r)
                            rcformula = rc.getFormula()
                            for u in nu[1]:
                                rc.applyUnifier(u)
                            rc2formula = rc.getFormula()
                            if rcformula != rc2formula:
                                changed = True
                                if env.debug:
                                    print(f"# (xform {t.getFormula})")
                                    print(f"# Program Line {p.getFormula()}")
                                    print(f"# Matched Node {nu[0].getFormula()}")
                                    print(f"# Transformed Node {rc2formula}")
                                if nu[0].id == p.id:
                                    p = rc
                                else:
                                    p.replaceNode(nu[0], rc)
            eval(p, env)
        i += 1


# Primitive Functions


def prefunc_debug(parentnode, env):
    env.debug = True
    return parentnode.next


def prefunc_xform(parentnode, env):
    global Transformations
    Transformations.append(parentnode.next)
    return None


PreFunctions = {"debug": prefunc_debug, "xform": prefunc_xform}


def nodefunc_if(node, env):
    global serial
    b = False
    dat=TreeNode(serial)
    serial+=1
    dat.data=copy.deepcopy(node.data)
    dat=eval(dat)
    if dat is None:
        b=False
    else:
        if type(dat) is DataNode:
            if dat.symbol=='true':
                b=True
            else:
                b=False
        else:
            if type(dat.data) is DataNode:
                if dat.data.symbol=='true':
                    b=True
                else:
                    b=False
    if b:
        if node.next:
            return node.next
        else:
            return None
    else:
        if node.next:
            if node.next.next:
                return node.next.next
            else:
                return None
        else:
            return None


NodeFunctions = {"if": nodefunc_if}


def func_print(args):
    for a in args[0]:
        print(f"{a}")
    return None


def func_add(args):
    if args is None:
        return None
    if len(args[0]) == 1:
        return args[0]
    r = args[0][0] + args[0][1]
    if len(args[0]) > 2:
        r = [r]
        r.extend(args[0][2:])
    return [r, TokenType.number]


def func_sub(args):
    if args is None:
        return None
    if len(args[0]) == 1:
        return args[0]
    r = args[0][0] - args[0][1]
    if len(args[0]) > 2:
        r = [r]
        r.extend(args[0][2:])
    return [r, TokenType.number]


def func_mult(args):
    if args is None:
        return None
    if len(args[0]) == 1:
        return args[0]
    r = args[0][0] * args[0][1]
    if len(args[0]) > 2:
        r = [r]
        r.extend(args[0][2:])
    return [r, TokenType.number]


def func_div(args):
    if args is None:
        return None
    if len(args[0]) == 1:
        return args[0]
    r = args[0][0] / args[0][1]
    if len(args[0]) > 2:
        r = [r]
        r.extend(args[0][2:])
    return [r, TokenType.number]


def func_concat(args):
    if args is None:
        return None
    return [" ".join(args[0]), TokenType.quoted_text]


def func_defFunc(args):
    if args is None:
        return None
    ParamFunctions[args[0][0]] = args[0][1].split()
    return None


ParamFunctions = {
    "print": func_print,
    "+": func_add,
    "-": func_sub,
    "*": func_mult,
    "/": func_div,
    "concat": func_concat,
    "op": func_defFunc,
}


def main():
    print(f"Brian v0.2 Copyright (c) 2023 Brian O'Dell")
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} program")
        sys.exit(1)
    program = loadFile(sys.argv[1])
    runProgram(program)


if __name__ == "__main__":
    main()
