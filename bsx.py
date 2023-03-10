import enum
import sys
import types
import copy
import seditor


Tokens = []
serial = 0
Transformations = []


class Environment:
    def __init__(self):
        self.debug = False
        self.debugindent = 0
        self.line = ""
        self.linenumber = 0
        self.vars = {}
        self.parent = None
        self.glob = []
        self.share=False


class TokenType(enum.Enum):
    parenopen = 1
    parenclose = 2
    constant = 3
    number = 4
    string = 5
    unknown = 6
    array=7


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
            if self.data.type == TokenType.string:
                formula += '"' + self.data.symbol + '" '
            else:
                formula += self.data.symbol + " "
        else:
            pass
        if self.next is not None:
            formula += self.next.getFormula()
        return formula

    def getString(self):
        s = ""
        if type(self.data) is TreeNode:
            s += self.data.getString() + " "
        elif type(self.data) is DataNode:
            if self.data.type==TokenType.number:
                s+=str(self.data.symbol) + " "
            else:
                s += self.data.symbol + " "
        else:
            pass
        if self.next is not None:
            s += self.next.getString()
        return s

    def getNSString(self):
        s = ""
        if type(self.data) is TreeNode:
            s += self.data.getNSString()
        elif type(self.data) is DataNode:
            if self.data.type==TokenType.number:
                s+=str(self.data.symbol)
            else:
                s += self.data.symbol
        else:
            pass
        if self.next is not None:
            s += self.next.getNSString()
        return s

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
            # if node.next:
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
        # elif c in "'":
        #     token = DataNode(TokenType.quote, "'", 0)
        #     tokens.append(token)
        elif c == '"':
            word = ""
            c = 0
            while index < len(formula) and c != '"':
                index += 1
                if index >= len(formula):
                    sys.exit(
                        f"Tokenization Error: End of quoted text not found in {formula}"
                    )
                c = formula[index]
                nc=0
                if index+1<len(formula):
                    nc=formula[index+1]
                else:
                    sys.exit(
                        f"Tokenization Error: End of quoted text not found in {formula}"
                    )
                if c=='\\' and nc=='"':
                    word+='"'
                    index+=1
                    if index>=len(formula):
                        sys.exit(
                            f"Tokenization Error: End of quoted text not found in {formula}"
                        )
                else:
                    word += c
            word = word[:-1]
            token = DataNode(TokenType.string, word, 0)
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


def eval(node, env):
    if node is None:
        return None
    if type(node.data) is DataNode:
        if node.data.symbol == "'":
            return node.next
        if node.data.symbol in Functions:
            func = Functions[node.data.symbol]
            node = func(node, env)
            if node is None:
                return None
            while type(node.data) is TreeNode and node.next is None:
                node=node.data
        if type(node.data) is DataNode:
            if node.data.symbol == "'":
                return node.next
    if env.share:
        env2=env
    else:
        env2 = copy.deepcopy(env)
        env2.parent = env
        env2.vars = {}
    dbug = " "
    if env.debug:
        print(f"# {dbug:<{env.debugindent*2}}NODE: {node.getFormula()}")
        env2.debugindent += 1
    if type(node.data) is TreeNode:
        node.data = eval(node.data, env2)
    node.next = eval(node.next, env2)
    if type(node.data) is DataNode:
        if node.data.symbol in Operators:
            if env.debug:
                print(f"# {dbug:<{env.debugindent*2}}OPERATION: {node.getFormula()}")
            func = Operators[node.data.symbol]
            x = func(node, env2)
            if env.debug:
                if x is None:
                    print(f"# {dbug:<{env.debugindent*2}}RESULT: None")
                else:
                    print(
                        f"# {dbug:<{env.debugindent*2}}RESULT: {x.getValue() if type(x) is DataNode else x.getString()}"
                    )
            return x
        return node

def transform(node, env):
    p=node
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
                        # if rcformula != rc2formula:
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
    return p



def runProgram(program, env):
    global Transformations
    i = 0
    while i < len(program):
        if type(program) is list:
            line = program[i]
            llist = line.split()
            while llist[-1] == "-":
                line = " ".join(llist[:-1])
                i += 1
                line += " " + program[i]
                llist = line.split()
        else:
            line=program
            i=len(program)
        t = tokenize(line)
        p = parse(t)
        if p is not None:
            p=transform(p, env)
            env.line = line
            env.linenumber = i+1
            eval(p, env)
        i += 1


# Primitive Functions and Operators

def getVarVal(var, env):
    if var in env.glob:
        p=env.parent
        while p:
            if var in p.vars:
                if p.vars[var][0] == TokenType.array:
                    sys.exit(f"ERROR: List Var {var} accessed as Scalar in line {env.linenumber} {env.line}")
                else:
                    return p.vars[var]
            p=p.parent
    else:
        if var in env.vars:
                if env.vars[var][0] == TokenType.array:
                    sys.exit(f"ERROR: List Var {var} accessed as Scalar in line {env.linenumber} {env.line}")
                else:
                    return env.vars[var]
    sys.exit(f"ERROR: Variable not defined but referenced in line {env.linenumber} {env.line}")

def getList(var, env):
    try:
        if var in env.glob:
            p=env.parent
            while p:
                if var in p.vars:
                    return p.vars[var]
                p=p.parent
        else:
            if var in env.vars:
                return env.vars[var]
        raise Exception()
    except Exception:
        sys.exit(f"ERROR: List not defined but referenced in line {env.linenumber} {env.line}")

def setList(var, val, env):
    if var in env.glob:
        p=env.parent
        while p:
            if var in p.vars:
                p.vars[var]=val
                return
            p=p.parent
    else:
        if var in env.vars:
            env.vars[var]=val
            return
    sys.exit(f"ERROR: List not defined but referenced in line {env.linenumber} {env.line}")


def func_debug(parentnode, env):
    env.debug = True
    return parentnode.next


def func_func(parentnode, env):
    global Transformations
    Transformations.append(parentnode.next)
    return None


def func_if(node, env):
    global serial
    b = False
    dat = TreeNode(serial)
    serial += 1
    try:
        dat.data = copy.deepcopy(node.next.data)
        dat = eval(dat, env)
    except:
        sys.exit(f"ERROR: if - missing operands in line {env.linenumber} {env.line}")

    if dat is None:
        b = False
    else:
        if type(dat) is DataNode:
            if dat.val != 0:
                b = True
            else:
                b = False
        else:
            if type(dat.data) is DataNode:
                if dat.data.val != 0:
                    b = True
                else:
                    b = False
    if b:
        try:
            node.next.next.next = None
            return node.next.next
        except:
            sys.exit(
                f"ERROR: if - missing operands in line {env.linenumber} {env.line}"
            )
    else:
        try:
            return node.next.next.next
        except:
            sys.exit(
                f"ERROR: if - missing operands in line {env.linenumber} {env.line}"
            )

def func_do(node, env):
    env.share=True
    return node.next

def func_parse(node, env):
    source=node.next.data.symbol
    rest=node.next.next
    newnode=parse(tokenize(source)).data
    newnode=transform(newnode, env)
    n=newnode
    while n.next:
        n=n.next
    n.next=rest 
    return newnode   


Functions = {
    "debug": func_debug, 
    "func": func_func, 
    "if": func_if, 
    "do": func_do,
    "parse":func_parse,
}


def op_print(node, env):
    try:
        s=node.next.getNSString().encode('latin-1','backslashreplace').decode('unicode-escape')
        print(s,end='')
    except:
        sys.exit(f"ERROR: print - missing operands in line {env.linenumber} {env.line}")
    return None

def op_newline(node, env):
    print('')

def op_number(node, env):
    try:
        if type(node.next.data) is DataNode:
            if node.next.data.type!=TokenType.number:
                node.next.data.type=TokenType.number
                try:
                    node.next.data.val=float(node.next.data.symbol)
                except:
                    node.next.data.val=0
                    node.next.data.symbol='0'
        return node.next.data
    except:
        sys.exit(f"ERROR: # - missing operands in line {env.linenumber} {env.line}")


def op_add(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = a + b
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: + - missing operands in line {env.linenumber} {env.line}")


def op_sub(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = a - b
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: - - missing operands in line {env.linenumber} {env.line}")


def op_mult(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = a * b
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: * - missing operands in line {env.linenumber} {env.line}")


def op_div(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = a / b
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: / - missing operands in line {env.linenumber} {env.line}")


def op_eq(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = 1 if a == b else 0
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: = - missing operands in line {env.linenumber} {env.line}")


def op_lteq(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = 1 if a <= b else 0
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: <= - missing operands in line {env.linenumber} {env.line}")


def op_gteq(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = 1 if a >= b else 0
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: >= - missing operands in line {env.linenumber} {env.line}")


def op_lt(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = 1 if a < b else 0
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: < - missing operands in line {env.linenumber} {env.line}")


def op_gt(node, env):
    try:
        a = node.next.data
        if a.type == TokenType.number:
            a = a.val
        else:
            a = getVarVal(a.symbol, env)[1]
        b = node.next.next.data
        if b.type == TokenType.number:
            b = b.val
        else:
            b = getVarVal(b.symbol, env)[1]
        c = 1 if a > b else 0
        return DataNode(TokenType.number, str(c), c)
    except:
        sys.exit(f"ERROR: > - missing operands in line {env.linenumber} {env.line}")


def op_string(node, env):
    try:
        c=node.next.getString()
        return DataNode(TokenType.string, c, 0)
    except:
        sys.exit(
            f"ERROR: $_ - missing operands in line {env.linenumber} {env.line}"
        )

def op_nbstring(node, env):
    try:
        c=node.next.getNSString()
        return DataNode(TokenType.string, c, 0)
    except:
        sys.exit(
            f"ERROR: $ - missing operands in line {env.linenumber} {env.line}"
        )

def op_input(node,env):
    if node.next:
        c=input(node.next.getString())
    else:
        c=input()
    d=DataNode(TokenType.string, c, 0)
    return d

def op_global(node, env):
    try:
        x=node.next
        while x:
            var=x.data.getValue()
            env.glob.append(var)
            p=env.parent
            while p:
                p.glob.append(var)
                p=p.parent
            x=x.next
    except:
        sys.exit(
            f"ERROR: global - missing operands in line {env.linenumber} {env.line}"
        )

def op_setvar(node, env):
    try:
        var = node.next.data.getValue()
        if type(node.next.next.data) is DataNode:
            val = [node.next.next.data.type, node.next.next.data.getValue()]
        else:
            val = [TokenType.string, node.next.next.data.getString()]
        if var in env.glob:
            p = env.parent
            while p.parent:
                p=p.parent
            p.vars[var] = val
        else:
            env.vars[var] = val
        return DataNode(val[0], val[1], val[1] if val[0] == TokenType.number else 0)
    except:
        sys.exit(
            f"ERROR: setvar - missing operands in line {env.linenumber} {env.line}"
        )

def op_getvar(node, env):
    if type(node.next.data) is DataNode:
        val = getVarVal(node.next.data.getValue(), env)
        return DataNode(val[0], val[1], val[1] if val[0] == TokenType.number else 0)
    sys.exit(f"ERROR: getvar - missing operands in line {env.linenumber} {env.line}")

    
def op_createlist(node, env):
    try:
        var=node.next.data.getValue()
        val=[]
        n=node.next.next
        while n:
            val.append(n.getNSString())
            n=n.next
        val=[TokenType.array, val]
        if var in env.glob:
            p = env.parent
            while p.parent:
                p=p.parent
            p.vars[var] = val
        else:
            env.vars[var] = val
        return None
    except:
        sys.exit(
            f"ERROR: [] - missing operands in line {env.linenumber} {env.line}"
        )

def op_getindexlist(node, env):
    try:
        var=node.next.data.getValue()
        index=int(node.next.next.data.getValue())
    except:
        sys.exit(
            f"ERROR: [@] - missing operands in line {env.linenumber} {env.line}"
        )
    val=getList(var, env)[1][index]
    return DataNode(TokenType.string, val, 0)



def op_getlistasstring(node, env):
    try:
        var=node.next.data.getValue()
    except:
        sys.exit(
            f"ERROR: [@] - missing operands in line {env.linenumber} {env.line}"
        )
    val=getList(var, env)[1]
    content='\r\n'.join(val)
    return DataNode(TokenType.string, content, 0)


def op_setindexlist(node, env):
    try:
        var=node.next.data.getValue()
        index=int(node.next.next.data.getValue())
        newval=node.next.next.next.data.getValue()
        val=getList(var, env)
        if index>=len(val[1]) or index<0 or len(val[1])==0:
            val[1].append(newval)
        else:
            val[1][index]=newval
        setList(var, val, env)
        return None
    except:
        sys.exit(
            f"ERROR: [!] - missing operands in line {env.linenumber} {env.line}"
        )

def op_delindexlist(node, env):
    try:
        var=node.next.data.getValue()
        index=int(node.next.next.data.getValue())
        val=getList(var, env)
        if index<len(val):
            val[1].pop(index)
        else:
            return None
        setList(var, val, env)
        return None
    except:
        sys.exit(
            f"ERROR: [-] - missing operands in line {env.linenumber} {env.line}"
        )


def op_lenlist(node, env):
    try:
        var=node.next.data.getValue()
        val=getList(var, env)
        return DataNode(TokenType.number, '', len(val[1]))
    except:
        sys.exit(
            f"ERROR: [#] - missing operands in line {env.linenumber} {env.line}"
        )


def op_delvar(node, env):
    try:
        var=node.next.data.getValue()
        x=env
        while x:
            if var in x.vars:
                x.vars.pop(var)
            if var in x.glob:
                x.glob.remove(var)
            x=x.parent
        return None
    except:
        sys.exit(
            f"ERROR: del - missing operands in line {env.linenumber} {env.line}"
        )


def op_op(node, env):
    try:
        formula = node.next.data.symbol
    except:
        sys.exit(f"ERROR: op - missing operands in line {env.linenumber} {env.line}")


def op_loop(node, env):
    env.share=True
    try:
        min = node.next.data.val
        max = node.next.next.data.val
        inc = node.next.next.next.data.val
        repeat = node.next.next.next.next
        while min < max:
            result = eval(copy.deepcopy(repeat), env)
            min += inc
        return None
    except:
        sys.exit(f"ERROR: loop - missing operands in line {env.linenumber} {env.line}")


def op_include(node, env):
    try:
        incfile=node.next.data.symbol
        program=loadFile(incfile)
        runProgram(program, env)
    except:
        sys.exit(f"ERROR: include - missing operands in line {env.linenumber} {env.line}")
 

def op_eval(node, env):
    try:
        source=getVarVal(node.next.data.symbol, env)[1]
    except:
        source=node.next.data.symbol
    try:
        runProgram(source, env)
        return None
    except:
        sys.exit(f"ERROR: eval - cannot evaluate operands in line {env.linenumber} {env.line}")

def op_seditor(node, env):
    try:
        var=node.next.data.getValue()
        val=getList(var, env)
        content=val[1]
        e=seditor.Editor()
        e.init_tty()
        e.set_lines(content)
        e.loop()
        e.deinit_tty()
        content=e.content
        val[1]=content
        setList(var, val, env)
        return None
    except:
        sys.exit(f"ERROR: seditor - cannot evaluate operands in line {env.linenumber} {env.line}")


Operators = {
    "print": op_print,
    "nl": op_newline,
    "#": op_number,
    "+": op_add,
    "-": op_sub,
    "*": op_mult,
    "/": op_div,
    "=": op_eq,
    ">=": op_gteq,
    "<=": op_lteq,
    ">": op_gt,
    "<": op_lt,
    "$_": op_string,
    "$": op_nbstring,
    "input": op_input,
    "global": op_global,
    "!": op_setvar,
    "@": op_getvar,
    "[]": op_createlist,
    "[]$": op_getlistasstring,
    "[!]": op_setindexlist,
    "[@]": op_getindexlist,
    "[-]": op_delindexlist,
    "[#]": op_lenlist,
    "del": op_delvar,
    "op": op_op,
    "loop": op_loop,
    "include": op_include,
    "eval": op_eval,
    "seditor": op_seditor,
}

def main():
    s='\033[37m'
    print(s, end='')
    print(f"Brian v0.2 Copyright (c) 2023 Brian O'Dell")
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} program")
        sys.exit(1)
    program = loadFile(sys.argv[1])
    runProgram(program, Environment())


if __name__ == "__main__":
    main()
