import os

import codecs
import javalang
#from ast import nodes
#from graphviz import Digraph
import json
import pickle
from tqdm import tqdm
import numpy as np
from run import *
from stringfycode import stringfyRoot
from copy import deepcopy
import time
import io
import subprocess
from Searchnode import Node
import traceback
import json
linenode = ['Statement_ter', 'BreakStatement_ter', 'ReturnStatement_ter', 'ContinueStatement', 'ContinueStatement_ter', 'LocalVariableDeclaration', 'condition', 'control', 'BreakStatement', 'ContinueStatement', 'ReturnStatement', "parameters", 'StatementExpression', 'return_type']
#os.environ["CUDA_VISIBLE_DEVICES"]="1, 4"
def getLocVar(node):
  varnames = []
  if node.name == 'VariableDeclarator':
    currnode = -1
    for x in node.child:
      if x.name == 'name':
        currnode = x
        break
    varnames.append((currnode.child[0].name, node))
  if node.name == 'FormalParameter':
    currnode = -1
    for x in node.child:
      if x.name == 'name':
        currnode = x
        break
    varnames.append((currnode.child[0].name, node))
  if node.name == 'InferredFormalParameter':
    currnode = -1
    for x in node.child:
      if x.name == 'name':
        currnode = x
        break
    varnames.append((currnode.child[0].name, node))
  for x in node.child:
    varnames.extend(getLocVar(x))
  return varnames
n = 0
def setid(root):
  global n
  root.id = n
  n += 1
  for x in root.child:
    setid(x)
def solveLongTree(root, subroot):
    global n
    m = 'None'
    troot = 'None'
    for x in root.child:
        if x.name == 'name':
            m = x.child[0].name
    if len(root.getTreestr().strip().split()) >= 1000:
        tmp = subroot
        if len(tmp.getTreestr().split()) >= 1000:
            assert(0)
        lasttmp = None
        while True:
            if len(tmp.getTreestr().split()) >= 1000:
                break
            lasttmp = tmp
            tmp = tmp.father
        index = tmp.child.index(lasttmp)
        ansroot = Node(tmp.name, 0)
        ansroot.child.append(lasttmp)
        ansroot.num = 2 + len(lasttmp.getTreestr().strip().split())
        while True:
            b = True
            afternode = tmp.child.index(ansroot.child[-1]) + 1
            if afternode < len(tmp.child) and ansroot.num + tmp.child[afternode].getNum() < 1000:
                b = False
                ansroot.child.append(tmp.child[afternode])
                ansroot.num += tmp.child[afternode].getNum()
            prenode = tmp.child.index(ansroot.child[0]) - 1
            if prenode >= 0 and ansroot.num + tmp.child[prenode].getNum() < 1000:
                b = False
                ansroot.child.append(tmp.child[prenode])
                ansroot.num += tmp.child[prenode].getNum()
            if b:
                break
        troot = ansroot
    else:
        troot = root
    n = 0
    setid(troot)
    varnames = getLocVar(troot)
    fnum = -1
    vnum = -1
    vardic = {}
    vardic[m] = 'meth0'
    typedic = {}
    for x in varnames:
        if x[1].name == 'VariableDeclarator':
            vnum += 1
            vardic[x[0]] = 'loc' + str(vnum)
            t = -1
            for s in x[1].father.father.child:
                #print(s.name)
                if s.name == 'type':
                    t = s.child[0].child[0].child[0].name[:-4]
                    break
            assert(t != -1)
            typedic[x[0]] = t
        else:
            fnum += 1
            vardic[x[0]] = 'par' + str(fnum)
            t = -1
            for s in x[1].child:
                if s.name == 'type':
                    t = s.child[0].child[0].child[0].name[:-4]
                    break
            assert(t != -1)
            typedic[x[0]] = t
    return troot, vardic, typedic
def addter(root):
    if len(root.child) == 0:
        root.name += "_ter"
    for x in root.child:
        addter(x)
    return
def setProb(r, p):
    r.possibility =  p#max(min(np.random.normal(0.8, 0.1, 10)[0], 1), 0)
    for x in r.child:
        setProb(x, p)
def getLineNode(root, block, add=True):
  ans = []
  block = block + root.name
  #print(root.name, 'lll')
  for x in root.child:
    if x.name in linenode:
      if 'info' in x.getTreestr() or 'assert' in x.getTreestr() or 'logger' in x.getTreestr() or 'LOGGER' in x.getTreestr() or 'system.out' in x.getTreestr().lower():
        continue
      x.block = block
      ans.append(x)
    else:
      #print(x.name)
      s = ""
      if not add:
        s = block
        #tmp = getLineNode(x, block)
      else:
        s = block + root.name
      #print(block + root.name + "--------")
      tmp = getLineNode(x, block)
      '''if x.name == 'then_statement' and tmp == []:
        print(tmp)
        print(x.father.printTree(x.father))
        assert(0)'''
      ans.extend(tmp)
  return ans
def getroottree(tokens, isex=False):
    if isinstance(tokens[0], tuple):
        root = Node(tokens[0][0], 0)
    else:
        root = Node(tokens[0], 0)
    currnode = root
    idx = 1
    for i, x in enumerate(tokens[1:]):
        if x != "^":
            if isinstance(x, tuple):
                nnode = Node(x[0], idx)
                nnode.position = x[1]
            else:
                nnode = Node(x, idx)
            nnode.father = currnode
            currnode.child.append(nnode)
            currnode = nnode
            idx += 1
        else:
            currnode = currnode.father
    return root
def ismatch(root, subroot):
    index = 0
    #assert(len(subroot.child) <= len(root.child))
    #print(len(subroot.child), len(root.child))
    for x in subroot.child:
        while index < len(root.child) and root.child[index].name != x.name:
            index += 1
        if index == len(root.child):
            return False
        if not ismatch(root.child[index], x):
            return False
        index += 1
    return True
def findSubtree(root, subroot):
    if root.name == subroot.name:
        if ismatch(root, subroot):
            return root
    for x in root.child:
        tmp = findSubtree(x, subroot)
        if tmp:
            return tmp
    return None
def generateAST(tree):
    sub = []
    if not tree:
        return ['None', '^']
    if isinstance(tree, str):
        tmpStr = tree
        tmpStr = tmpStr.replace(" ", "").replace(":", "")
        if "\t" in tmpStr or "'" in tmpStr or "\"" in tmpStr:
            tmpStr = "<string>"
        if len(tmpStr) == 0:
            tmpStr = "<empty>"
        if tmpStr[-1] == "^":
            tmpStr += "<>"
        sub.append(tmpStr)
        sub.append("^")
        return sub
    if isinstance(tree, list):
        if len(tree) == 0:
            sub.append("empty")
            sub.append("^")
        else:
            for ch in tree:
                subtree = generateAST(ch)
                sub.extend(subtree)
        return sub
    position = None
    if hasattr(tree, 'position'):
        #assert(0)
        position = tree.position
    curr = type(tree).__name__
    #print(curr)
    if True:
        if False:
            assert(0)#sub.append((str(getLiteral(tree.children)))
        else:
            sub.append((curr, position))
            try:
                for x in tree.attrs:
                    if x == "documentation":
                        continue
                    if not getattr(tree, x):
                        continue
                    '''if x == 'prefix_operators':
                        node = getattr(tree, x)
                        print(type(node))
                        print(len(node))
                        print(node[0])
                        assert(0)
                    if type(getattr(tree, x)).__name__ not in nodes:
                        print(type(getattr(tree, x)).__name__)
                        continue'''
                    sub.append(x)
                    node = getattr(tree, x)
                    if isinstance(node, list):
                        if len(node) == 0:
                            sub.append("empty")
                            sub.append("^")
                        else:
                            for ch in node:
                                subtree = generateAST(ch)
                                sub.extend(subtree)
                    elif isinstance(node, javalang.tree.Node):
                        subtree = generateAST(node)
                        sub.extend(subtree)
                    elif not node:
                        continue
                    elif isinstance(node, str):
                        tmpStr = node
                        tmpStr = tmpStr.replace(" ", "").replace(":", "")
                        if "\t" in tmpStr or "'" in tmpStr or "\"" in tmpStr:
                            tmpStr = "<string>"
                        if len(tmpStr) == 0:
                            tmpStr = "<empty>"
                        if tmpStr[-1] == "^":
                            tmpStr += "<>"
                        sub.append(tmpStr)
                        sub.append("^")
                    elif isinstance(node, set):
                        for ch in node:
                            subtree = generateAST(ch)
                            sub.extend(subtree)
                    elif isinstance(node, bool):
                        sub.append(str(node))
                        sub.append("^")
                    else:
                        #print(type(node))
                        assert(0)
                    sub.append("^")
            except AttributeError:
                assert(0)
                pass
        sub.append('^')
        return sub
    else:
        #print(curr)
        pass
    return sub
def getroottree2(tokens, isex=False):
    root = Node(tokens[0], 0)
    currnode = root
    idx = 1
    for x in tokens[1:]:
        if x != "^":
            nnode = Node(x, idx)
            nnode.father = currnode
            currnode.child.append(nnode)
            currnode = nnode
            idx += 1
        else:
            currnode = currnode.father
    return root
'''def setProb(root, subroot, prob):
    root.possibility = max(min(max(root.possibility, prob), 0.98), 0.01)
    index = 0
    assert(len(subroot.child) <= len(root.child))
    #print(len(subroot.child), len(root.child))
    for x in subroot.child:
        while root.child[index].name != x.name:
            #print(root.child[index].name, x.name)
            index += 1
        setProb(root.child[index], x, prob)
        index += 1'''
def getSubroot(treeroot):
    currnode = treeroot
    lnode = None
    mnode = None
    while currnode:
        if currnode.name in linenode:
            lnode = currnode
            break
        currnode = currnode.father
    currnode = treeroot
    while currnode:
        if currnode.name == 'MethodDeclaration' or currnode.name == 'ConstructorDeclaration':
            mnode = currnode
            break
        currnode = currnode.father
    return lnode, mnode
def getNodeById(root, line):
    if root.position:
        if root.position.line == line and root.name != 'IfStatement' and root.name != 'ForStatement' and root.name != 'WhileStatement':
            return root
    for x in root.child:
        t = getNodeById(x, line)
        if t:
            return t
    return None
def containID(root):
    ans = []
    if root.position is not None:
        ans.extend([root.position.line])
    for x in root.child:
        ans.extend(containID(x))
    return ans
def getAssignMent(root):
    if root.name == 'Assignment':
        return root
    for x in root.child:
        t = getAssignMent(x)
        if t:
            return t
    return None
def isAssign(line):
    #sprint(4, line.getTreestr())
    if 'Assignment' not in line.getTreestr():
        return False
    anode = getAssignMent(line)
    if anode.child[0].child[0].name == 'MemberReference' and anode.child[1].child[0].name == 'MethodInvocation':
        try:
            m = anode.child[0].child[0].child[0].child[0].name
            v = anode.child[1].child[0].child[0].child[0].name
        except:
            return False
        print(m, v)
        return m == v
    if anode.child[0].child[0].name == 'MemberReference':
        try:
            m = anode.child[0].child[0].child[0].child[0].name
        except:
            return False
        if "qualifier " + m in anode.child[1].getTreestr():
            return True
    return False
import time

def testone(ssize,testmodel,filepath,lineid):
    model = testmodel
    st = time.time()
    lines1 = open(filepath, "r").read()
    liness = lines1.splitlines()
    tokens = javalang.tokenizer.tokenize(lines1)
    parser = javalang.parser.Parser(tokens)
    tree = parser.parse_member_declaration()
    
    tmproot = getroottree(generateAST(tree))
    currroot = getNodeById(tmproot, lineid)
    # print(currroot.printTree(currroot))
    lnode, mnode = getSubroot(currroot)
    oldcode = liness[lineid - 1]
    subroot = lnode
    treeroot = mnode
    presubroot = None
    aftersubroot = None     
    linenodes = getLineNode(treeroot, "")
    currid = linenodes.index(subroot)
    if currid > 0:
        presubroot = linenodes[currid - 1]
    if currid < len(linenodes) - 1:
        aftersubroot = linenodes[currid + 1]
    setProb(treeroot, 2)
    addter(treeroot)
    data = []
    if True:
        setProb(treeroot, 2)
        if subroot is not None:
            setProb(subroot, 1)
        if aftersubroot is not None:
            setProb(aftersubroot, 4)
        if presubroot is not None:
            setProb(presubroot, 3)
                    #print(containID(subroot))
        cid = set(containID(subroot))
        maxl = -1
        minl = 1e10
        for l in cid:
            maxl = max(maxl, l - 1)
            minl = min(minl, l - 1)
                    #print(maxl, liness[maxl + 1])
        precode = "\n".join(liness[0:minl])
        aftercode = "\n".join(liness[maxl + 1:])
        oldcode = "\n".join(liness[minl:maxl + 1])
        troot, vardic, typedic = solveLongTree(treeroot, subroot)
        data.append({'treeroot':treeroot, 'troot':troot, 'oldcode':oldcode, 'filepath':filepath, 'subroot':subroot, 'vardic':vardic, 'typedic':typedic, 'precode':precode, 'aftercode':aftercode, 'tree':troot.printTreeWithVar(troot, vardic), 'prob':troot.getTreeProb(troot), 'mode':0, 'line':lineid, 'isa':False})
   # print(time.time() - st)
   # print(time.time() - st)
    # print(2)
    ans = solveone2(data, model, ssize)
    # print(3)
    tans = []
    for p in ans:
        psss = p
        mode = p['mode']
        precode = p['precode']
        aftercode = p['aftercode']        
        oldcode = p['oldcode']
        root = getroottree2(p['code'].split())
        if mode == 1:
            aftercode = oldcode + aftercode
        lines = aftercode.splitlines()
        if 'throw' in lines[0] and mode == 1:
            for s, l in enumerate(lines):
                if 'throw' in l or l.strip() == "}":
                    precode += l + "\n"
                else:
                    break
            aftercode = "\n".join(lines[s:])
        if lines[0].strip() == '}' and mode == 1:
            precode += lines[0] + "\n"
            aftercode = "\n".join(lines[1:])

        try:
            code = stringfyRoot(root, False, mode)
        except:
            print(traceback.print_exc())
            continue
        if '<string>' in code:
            if '\'.\'' in oldcode:
                code = code.replace("<string>", '"."')
            elif '\'-\'' in oldcode:
                code = code.replace("<string>", '"-"')
            elif '\"class\"' in oldcode:
                code = code.replace("<string>", '"class"')
            elif 'f-12' in oldcode:
                code = code.replace('<string>', 'f-12')
            else:
                code = code.replace("<string>", "\"null\"")
        if len(root.child) > 0 and root.child[0].name == 'condition' and mode == 0:
            if 'while' in oldcode:
                code = 'while' + code + "{"
            else:
                code = 'if' + code + "{"
        if code == "" and 'for' in oldcode and mode == 0:
            code = oldcode + "if(0!=1)break;"
        lnum = 0
        for l in code.splitlines():
            if l.strip() != "":
                lnum += 1
            else:
                continue
        if 'ArrayList<Integer>' in oldcode:
            code = code.replace('ArrayList', 'ArrayList<Integer>')
        if mode == 1 and len(precode.splitlines()) > 0 and 'case' in precode.splitlines()[-1]:
            lines = precode.splitlines()
            for i in range(len(lines) - 2, 0, -1):
                if lines[i].strip() == '}':
                    break
            precode = "\n".join(lines[:i])
            aftercode = "\n".join(lines[i:]) + "\n" + aftercode
        if lnum == 1 and 'if' in code and mode == 1:
            if len(precode.splitlines()) > 0 and 'for' in precode.splitlines()[-1]:
                code = code + 'continue;\n}\n'    
            else:
                afterlines = aftercode.splitlines()
                lnum = 0
                rnum = 0
                ps = p
                for p, y in enumerate(afterlines):
                    if '{' in y:
                        lnum += 1
                    if '}' in y:
                        if lnum == 0:
                            aftercode = "\n".join(afterlines[:p] + ['}'] + afterlines[p:])
                                #assert(0)
                            break
                        lnum -= 1
            tmpcode = precode + "\n" + code + aftercode
            tokens = javalang.tokenizer.tokenize(tmpcode)
            parser = javalang.parser.Parser(tokens)
        else:
            tmpcode = precode + "\n" + code + aftercode
            tokens = javalang.tokenizer.tokenize(tmpcode)
            parser = javalang.parser.Parser(tokens)
        tans.append({'code':tmpcode})
    return tans
def load_model_for_test(model_path):
    dev_set = SumDataset(args, "test")
    rulead = gVar(pickle.load(open("/root/zwk/Recoder_models/rulead.pkl", "rb"))).float().unsqueeze(0).repeat(2, 1, 1)
    args.cnum = rulead.size(1)
    tmpast = getAstPkl(dev_set)
    a, b = getRulePkl(dev_set)
    tmpf = gVar(a).unsqueeze(0).repeat(2, 1).long()
    tmpc = gVar(b).unsqueeze(0).repeat(2, 1, 1).long()
    tmpindex = gVar(np.arange(len(dev_set.ruledict))).unsqueeze(0).repeat(2, 1).long()
    tmpchar = gVar(tmpast).unsqueeze(0).repeat(2, 1, 1).long()
    tmpindex2 = gVar(np.arange(len(dev_set.Code_Voc))).unsqueeze(0).repeat(2, 1).long()
    # print(len(dev_set))
    args.Nl_Vocsize = len(dev_set.Nl_Voc)
    args.Code_Vocsize = len(dev_set.Code_Voc)
    args.Vocsize = len(dev_set.Char_Voc)
    args.rulenum = len(dev_set.ruledict) + args.NlLen

    print("NL_voc: "+str(args.Nl_Vocsize))
    print("code_voc: " + str(args.Code_Vocsize))
    print("voc_size: " + str(args.Vocsize))
    print("rule_num: " + str(args.rulenum))
    model = Decoder(args)
    if torch.cuda.is_available():
        print('using GPU')
        # os.environ["CUDA_VISIBLE_DEVICES"] = "3"
        model = model.cuda()
    model = model.eval()
    model.load_state_dict(torch.load(model_path))
    return model

def fix_benchmarks(model_path,benchmarks_dir,search_size,fix_dir):
    model=load_model_for_test(model_path)
    d4j_ids=codecs.open(benchmarks_dir+'/d4j.ids').readlines()
    bdj_ids=codecs.open(benchmarks_dir+'/bdj.ids').readlines()
    bears_ids = codecs.open(benchmarks_dir + '/bears.ids').readlines()
    qbs_ids = codecs.open(benchmarks_dir + '/qbs.ids').readlines()
    print("total "+str(len(d4j_ids)+len(bdj_ids)+len(bears_ids)+len(qbs_ids))+" bugs")
    d4j_failed=[]
    bdjar_failed=[]
    bears_failed=[]
    qbs_failed=[]
    for i,id in enumerate(d4j_ids):
        print("d4j "+str(i))
        id=id.strip()
        buggyfile=benchmarks_dir+'/buggy_methods/d4j_'+id+".txt"
        metas=codecs.open(benchmarks_dir+'/metas/d4j_'+id+'.txt').read()
        buggy_lineid=int(str(metas.split('<sep>')[2]).replace('[','').split(':')[0])+1
        print(buggy_lineid)

        fixs = testone(search_size, model, buggyfile, buggy_lineid)  # list:dict:({'code':tmpcode, 'ast':psss['otree']})
        fix_dict = {}
        # get patch_code
        for idx, fix in enumerate(fixs):
            fix_dict[idx] = fix["code"]
        patch_f = codecs.open(fix_dir + '/d4j_' + id + '.fix', 'w', encoding='utf8')
        patch_f.write(json.dumps(fix_dict))

        try:
            fixs = testone(search_size, model, buggyfile,buggy_lineid)  # list:dict:({'code':tmpcode, 'ast':psss['otree']})
            fix_dict={}
            # get patch_code
            for idx,fix in enumerate(fixs):
                fix_dict[idx]=fix["code"]
            patch_f=codecs.open(fix_dir+'/d4j_'+id+'.fix','w',encoding='utf8')
            patch_f.write(json.dumps(fix_dict))
        except:
            print("failed")
            d4j_failed.append(id+'\n')

    for i,id in enumerate(bdj_ids):
        print("bdj " + str(i))
        id = id.strip()
        buggyfile=benchmarks_dir+'/buggy_methods/bdjar_'+id+".txt"
        metas=codecs.open(benchmarks_dir+'/metas/bdjar_'+id+'.txt').read()
        buggy_lineid=int(str(metas.split('<sep>')[2]).replace('[','').split(':')[0])+1
        print(buggy_lineid)
        try:
            fixs = testone(search_size, model, buggyfile,buggy_lineid)  # list:dict:({'code':tmpcode, 'ast':psss['otree']})
            fix_dict={}
            # get patch_code
            for idx,fix in enumerate(fixs):
                fix_dict[idx]=fix["code"]
            patch_f=codecs.open(fix_dir+'/bdjar_'+id+'.fix','w',encoding='utf8')
            patch_f.write(json.dumps(fix_dict))
        except:
            bdjar_failed.append(id+'\n')
    for i,id in enumerate(bears_ids):
        print("bears " + str(i))
        id = id.strip()
        buggyfile=benchmarks_dir+'/buggy_methods/bears_'+id+".txt"
        metas=codecs.open(benchmarks_dir+'/metas/bears_'+id+'.txt').read()
        buggy_lineid=int(str(metas.split('<sep>')[2]).replace('[','').split(':')[0])+1
        print(buggy_lineid)
        try:
            fixs = testone(search_size, model, buggyfile,buggy_lineid)  # list:dict:({'code':tmpcode, 'ast':psss['otree']})
            fix_dict={}
            # get patch_code
            for idx,fix in enumerate(fixs):
                fix_dict[idx]=fix["code"]
            patch_f=codecs.open(fix_dir+'/bears_'+id+'.fix','w',encoding='utf8')
            patch_f.write(json.dumps(fix_dict))
        except:
            bears_failed.append(id+'\n')
    for i,id in enumerate(qbs_ids):
        print("qbs " + str(i))
        id = id.strip()
        buggyfile=benchmarks_dir+'/buggy_methods/qbs_'+id+".txt"
        metas=codecs.open(benchmarks_dir+'/metas/qbs_'+id+'.txt').read()
        buggy_lineid=int(str(metas.split('<sep>')[2]).replace('[','').split(':')[0])+1
        print(buggy_lineid)
        try:
            fixs = testone(search_size, model, buggyfile,buggy_lineid)  # list:dict:({'code':tmpcode, 'ast':psss['otree']})
            fix_dict={}
            # get patch_code
            for idx,fix in enumerate(fixs):
                fix_dict[idx]=fix["code"]
            patch_f=codecs.open(fix_dir+'/qbs_'+id+'.fix','w',encoding='utf8')
            patch_f.write(json.dumps(fix_dict))
        except:
            qbs_failed.append(id+'\n')
    d4j_failed_f=codecs.open(fix_dir+'/d4j_failed.txt','w',encoding='utf8')
    bdjar_failed_f = codecs.open(fix_dir + '/bdjar_failed.txt', 'w', encoding='utf8')
    bears_failed_f = codecs.open(fix_dir + '/bears_failed.txt', 'w', encoding='utf8')
    qbs_failed_f = codecs.open(fix_dir + '/qbs_failed.txt', 'w', encoding='utf8')
    d4j_failed_f.writelines(d4j_failed)
    bdjar_failed_f.writelines(bdjar_failed)
    bears_failed_f.writelines(bears_failed)
    qbs_failed_f.writelines(qbs_failed)





if __name__ == '__main__':
    import argparse
    fix_benchmarks("/root/zwk/Recoder_models/best_model.ckpt","/root/zwk/NPR_DATA0306/Evaluationdata/Benchmark",150,"/root/zwk/NPR_DATA0306/FixResults/Benchmark_ori")
    """"
    model = load_model_for_test("/root/zwk/NPR_DATA0306/Processed_Recoder/Model_save/checkpointSearch/best_model.ckpt")
    testdir = "./testdata"
    error_info = "/error_infos.txt"
    error_info_path = testdir + error_info
    errorinfolines = codecs.open(error_info_path, 'r', encoding='utf8').readlines()
    fail_info_path = testdir + "/fail_info.txt"
    failed = []
    patch_info_path = testdir + "/patch.txt"
    patch_fp = open(patch_info_path,"w")
    for info in tqdm(errorinfolines):
        fix_dict = {}
        infos = info.split("<SEP>")
        id = infos[0]

        buggy_lineid = int(infos[1])
        buggyfile = testdir + '/' + id + ".buggy"
        try:
            fixs = testone(10, model, buggyfile,buggy_lineid)  # list:dict:({'code':tmpcode, 'ast':psss['otree']})
            fix_dict["id"] = id
            code = []
            # get patch_code
            for fix in fixs:
                code.append(fix["code"])
            fix_dict["code"] = code
            patch_fp.write(json.dumps(fix_dict))
            patch_fp.write("\n")
        except:
            failed.append(id)
    patch_fp.close()
    fail_fp = open(fail_info_path, "w")
    for line in failed:
        fail_fp.write(line)
        fail_fp.write("'\n'")
    fail_fp.close()
    #print(time.time() - st)
    #open("ans.txt", "w").write("\n\n-------\n\n".join(tans))
    """
