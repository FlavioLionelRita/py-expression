import re
from .base import *
from .coreLib import CoreLib

class SourceManager():
    def __init__(self,model):
        self._model=model
        self._libraries={}

    @property
    def model(self):
        return self._model

    @property
    def libraries(self):
        return self._libraries     

    def addLibrary(self,library):
        self._libraries[library.name] =library

        for name in library.enums:
            self._model.addEnum(name,library.enums[name])

        for name in library.operators:
            operator= library.operators[name]
            for cardinality in operator:
                data = operator[cardinality]
                self._model.addOperator(name,cardinality,data['metadata'])    

        for name in library.functions:
            data = library.functions[name]
            self._model.addFunction(name,data['metadata'])        
  
    def nodeToOperand(self,node:Node)->Operand:
        children = []
        for p in node.children:
            child = self.nodeToOperand(p)
            children.append(child)
        operand = self.createOperand(node.name,node.type,children)
        for i,p in enumerate(operand.children):
            p.parent = operand
            p.index = i
            p.level = operand.level +1
        return operand 

    def reduce(self,operand:Operand):
        """ if all the children are constant, reduce the expression a constant """
        if isinstance(operand,Operator):        
            allConstants=True              
            for p in operand.children:
                if not isinstance(p,Constant):
                    allConstants=False
                    break
            if  allConstants:
                value = operand.value                
                constant= Constant(value)
                constant.parent = operand.parent
                constant.index = operand.index
                return constant
            else:
                for i, p in enumerate(operand.children):
                   operand.children[i]=self.reduce(p)
        return operand  

    def createOperand(self,name:str,type:str,children:list[Operand])->Operand:
        if type == 'constant':
            return Constant(name,children)
        elif type == 'variable':
            return Variable(name,children)
        elif type == 'keyValue':
            return KeyValue(name,children)
        elif type == 'array':
            return Array(name,children)
        elif type == 'object':
            return Object(name,children)
        elif type == 'operator':
            return self.createOperator(name,children)
        elif type == 'function':
            return self.createFunction(name,children)
        elif type == 'arrowFunction':
            return self.createArrowFunction(name,children)
        elif type == 'childFunction':
            if name in self.model.functions:
                return self.createFunction(name,children)
            else:
               return ContextFunction(name,children)
        elif type == 'block':
            return  Block(name,children)
        elif type == 'if':
            return  If(name,children)
        elif type == 'while':
            return  While(name,children)
        else:
            raise ExpressionError('node: '+name +' not supported') 

    def createOperator(self,name:str,children:list[Operand])->Operator:
        try:
            cardinality =len(children)
            metadata = self._model.getOperatorMetadata(name,cardinality)
            if metadata['lib'] in self._libraries:
                implementation= self._libraries[metadata['lib']].operators[name][cardinality]
                if implementation['custom'] is not None:                    
                    return implementation['custom'](name,children,implementation['customFunction']) 
                else:
                    function= implementation['function']
                    return Operator(name,children,function)
            return None        
        except:
            raise ModelError('error with operator: '+name)  

    def createFunction(self,name:str,children:list[Operand])->Function:
        try:            
            metadata = self._model.getFunctionMetadata(name)
            if metadata['lib'] in self._libraries:
                implementation= self._libraries[metadata['lib']].functions[name]
                if implementation['custom'] is not None:                   
                    return implementation['custom'](name,children) 
                else:
                    function= implementation['function']
                    return Function(name,children,function)
            return None
        except:
            raise ModelError('error with function: '+name) 

    def createArrowFunction(self,name:str,children:list[Operand]):
        try:            
            metadata = self._model.getFunctionMetadata(name)
            if metadata['lib'] in self._libraries:
                implementation= self._libraries[metadata['lib']].functions[name]
                if implementation['custom'] is not None:                    
                    return implementation['custom'](name,children) 
                else:
                    function= implementation['function']
                    return ArrowFunction(name,children,function)
            return None
        except:
            raise ModelError('error with function: '+name)              

    def compile(self,node:Node):
        operand =self.nodeToOperand(node)
        operand =self.reduce(operand)
        return operand

    def run(self,operand:Operand,context:dict={})-> any :  
        if context is not None:
            self.setContext(operand,Context(context))
        return operand.value

    def setContext(self,operand:Operand,context:Context):
        current = context
        if issubclass(operand.__class__,ChildContextable):
            childContext=current.newContext()
            operand.context = childContext
            current = childContext
        elif issubclass(operand.__class__,Contextable):
            operand.context = current       
        for p in operand.children:
            self.setContext(p,current) 

         
    def vars(self,operand:Operand)->dict:
        list = {}
        if isinstance(operand,Variable):
            list[operand.name] = self.operandType(operand)
        for p in operand.children:
            if isinstance(p,Variable):
                list[p.name] = self.operandType(p)
            elif len(p.children)>0:
                subList= self.vars(p)
                list = {**list, **subList}
        return list 

    def operandType(self,operand:Operand)->str:
        """ """
        if isinstance(operand.parent,Operator):
            metadata = self._model.getOperatorMetadata(operand.parent.name,len(operand.parent.children))
            if metadata['category'] == 'comparison':
                otherIndex = 1 if operand.index == 0 else 0
                otherOperand= operand.parent.children[otherIndex]
                if isinstance(otherOperand,Constant):
                    return otherOperand.type
                elif isinstance(otherOperand,Function):    
                    metadata =self.getFunctionMetadata(otherOperand.name)
                    return metadata['return']
                elif isinstance(otherOperand,Operator):    
                    metadata =self._model.getOperatorMetadata(otherOperand.name,len(otherOperand.children))
                    return metadata['return']    
                else:
                    return 'any'
            else:        
                return metadata['args'][operand.index]['type']
        elif isinstance(operand.parent,Function):
            name = operand.parent.name.replace('.','',1) if operand.parent.name.starWith('.') else  operand.parent.name
            metadata =self._model.getFunctionMetadata(name)
            return metadata['args'][operand.index]['type'] 

    def constants(self,operand:Operand)->dict:
        list = {}
        if isinstance(operand,Constant):
            list[operand.value] = operand.type
        for p in operand.children:
            if isinstance(p,Constant):
                list[p.value] = p.type
            elif len(p.children)>0:
                subList= self.constants(p)
                list = {**list, **subList}
        return list
    
    def operators(self,operand:Operand)->dict:
        list = {}
        if isinstance(operand,Operator):
            metadata = self._model.getOperatorMetadata(operand.name,len(operand.children)) 
            list[operand.name] = metadata['category']
        for p in operand.children:
            if isinstance(p,Operator):
                metadata = self._model.getOperatorMetadata(p.name,len(p.children)); 
                list[p.name] =  metadata['category']
            elif len(p.children)>0:
                subList= self.operators(p)
                list = {**list, **subList}
        return list

    def functions(self,operand:Operand)->dict:
        list = {}
        if isinstance(operand,Function):
            list[operand.name] = {}
        for p in operand.children:
            if isinstance(p,Function):
                list[p.name] = {}
            elif len(p.children)>0:
                subList= self.functions(p)
                list = {**list, **subList}

        for key in list:
            list[key] = self._model.functions[key]
        return list
      
    def serialize(self,operand:Operand)-> dict:
        children = []                
        for p in operand.children:
            children.append(self.serialize(p))
        return {'n':operand.name,'t':type(operand).__name__,'c':children} 

    def deserialize(self,serialized:dict)-> Operand:
        children = []
        if 'c' in serialized:
            for p in serialized['c']:
                children.append(self.deserialize(p))
        operand = self.createOperand(serialized['n'],serialized['t'],children)
        for i,p in enumerate(operand.children):
            p.parent = operand
            p.index = i
            p.level = operand.level +1
        return operand   

    def eval(self,operand:Operand,context:dict={},token:Token=None)-> any :  
        if context is not None:
            self.setContext(operand,Context(context))
        return operand.eval(token)

    # def degugger(self,operand:Operand,context:dict={})-> Debug:
    #     if context is not None:
    #         self.setContext(operand,Context(context))
    #     return self._degugger(operand) 

    # def _degugger(self,operand:Operand)-> Debug:
    #     children = []                
    #     for p in operand.children:
    #         children.append(self._degugger(p))
    #     return Debug(operand,children)    

    # def degug(self,debuggeable:Debug,token:Token):
    #     debuggeable.debug(token,0)        

    # def debug(self,token:Token,level): 
    #     if len(token.path) <= level:
    #         if len(self.children)== 0:
    #             token.value= self.value 
    #         else:
    #             token.path.append(0)
    #             self.children[0].debug(token,level+1)   
    #     else:
    #         idx = token.path[level]
    #         # si es el anteultimo nodo 
    #         if len(token.path) -1 == level:           
    #             if len(self.children) > idx+1:
    #                token.path[level] = idx+1
    #                self.children[idx+1].debug(token,level+1)
    #             else:
    #                token.path.pop() 
    #                token.value= self.value       
    #         else:
    #             self.children[idx].debug(token,level+1)  

    # def getOperandByPath(self,operand:Operand,path)->Operand:
    #     search = operand
    #     for p in path:
    #         if len(search.children) <= p:return None
    #         search = search.children[p]
    #     return search    
        
class NodeManager():
    def __init__(self,model):
       self._model = model    
          
    def vars(self,node:Node)->dict:
        list = {}
        if node.type == 'variable':
            list[node.name] = self.operandType(node)
        for p in node.children:
            if p.type =='variable':
                list[p.name] = self.operandType(p)
            elif len(p.children)>0:
                subList= self.vars(p)
                list = {**list, **subList}
        return list 

    def operandType(self,node:Node)->str:
        """ """
        if node.parent.type == 'operator':
            metadata = self._model.getOperatorMetadata(node.parent.name,len(node.parent.children))
            if metadata['category'] == 'comparison':
                otherIndex = 1 if node.index == 0 else 0
                otherOperand= node.parent.children[otherIndex]
                if otherOperand.type == 'constant':
                    return type(otherOperand.name).__name__ 
                elif otherOperand.type == 'function':    
                    metadata =self._model.getFunctionMetadata(otherOperand.name)
                    return metadata['return']
                elif otherOperand.type == 'operator':    
                    metadata =self._model.getOperatorMetadata(otherOperand.name,len(otherOperand.children))
                    return metadata['return']    
                else:
                    return 'any'
            else:        
                return metadata['args'][node.index]['type']
        elif node.parent.type == 'function':            
            metadata =self._model.getFunctionMetadata(node.parent.name)
            return metadata['args'][node.index]['type'] 

    def constants(self,node:Node)->dict:
        list = {}
        if node.type == 'constant':
            list[node.name] = type(node.name).__name__ 
        else:    
            for p in node.children:
                if p.type == 'constant':
                    list[p.name] = type(p.name).__name__ 
                elif len(p.children)>0:
                    subList= self.constants(p)
                    list = {**list, **subList}
        return list
    
    def operators(self,node:Node)->dict:
        list = {}
        if node.type ==  'operator':
            metadata = self._model.getOperatorMetadata(node.name,len(node.children)) 
            list[node.name] = metadata['category']
        for p in node.children:
            if p.type == 'operator':
                metadata = self._model.getOperatorMetadata(p.name,len(p.children)); 
                list[p.name] =  metadata['category']
            elif len(p.children)>0:
                subList= self.operators(p)
                list = {**list, **subList}
        return list

    def functions(self,node:Node)->dict:
        list = {}
        if node.type == 'function':
            list[node.name] = {}
        for p in node.children:
            if p.type == 'function':
                list[p.name] = {}
            elif len(p.children)>0:
                subList= self.functions(p)
                list = {**list, **subList}

        for key in list:
            list[key] = self._model.functions[key]
        return list

    def serialize(self,node:Node)-> dict:
        children = []                
        for p in node.children:
            children.append(self.serialize(p))
        return {'n':node.name,'t':node.type,'c':children} 

    def deserialize(self,serialized:dict)-> Node:
        children = []
        if 'c' in serialized:
            for p in serialized['c']:
                children.append(self.deserialize(p))
        node=  Node(serialized['n'],serialized['t'],children)
        for i,p in enumerate(node.children):
            p.parent = node
            p.index = i
        return node        

    def setParent(self,node:Node,parent:Node=None,index:int=0):
        node.parent = parent
        node.index = index
        if  len(node.children)>0:
            for i,p in enumerate(node.children):
                self.setParent(p,node,i)       

# Facade   
class Exp(metaclass=Singleton):
    def __init__(self):
       self.model = Model()
       self.parser = Parser(self.model)
       self.nodeManager = NodeManager(self.model)
       self.sourceManager = SourceManager(self.model)   
       self.addLibrary(CoreLib())        

    def addLibrary(self,library):
        self.sourceManager.addLibrary(library)
        self.refresh() 
    
    def refresh(self):
        self.parser.refresh()    
    
    def minify(self,expression:str)->str:
        isString=False
        quotes=None
        result =[]
        buffer = list(expression)
        for p in buffer:
            if isString and p == quotes: isString=False 
            elif not isString and (p == '\'' or p=='"'):
                isString=True
                quotes=p
            if (p != ' ' and p!='\n' and p!='\r' and p!='\t' ) or isString:
               result.append(p)
        return result
    
    def parse(self,expression:str)->Node:
        try:
            minified = self.minify(expression) 
            node= self.parser.parse(minified)
            self.nodeManager.setParent(node)
            return node
        except Exception as error:
            raise ExpressionError('expression: '+expression+' error: '+str(error))

    def compile(self,value)->Operand:
        try:
            node=None
            if isinstance(value,Node):
                node=value                
            elif isinstance(value,str):
                node = self.parse(value)
            else:
               raise ExpressionError('not possible to compile')      

            return self.sourceManager.compile(node)
        except Exception as error:
            raise ExpressionError('node: '+node.name+' error: '+str(error))  

    def run(self,value,context:dict={})-> any : 
        try:
            operand=None
            if isinstance(value,Operand):
                operand=value
            elif isinstance(value,Node):                
                operand =self.sourceManager.compile(value)                   
            elif isinstance(value,str):
                node = self.parse(value)
                operand =self.sourceManager.compile(node) 
            else:
               raise ExpressionError('not possible to run')  

            # return self.sourceManager.run(operand,context)
            return self.sourceManager.eval(operand,context)
        except Exception as error:
            raise ExpressionError('operand: '+operand.name+' error: '+str(error))               

    def eval(self,operand:Operand,context:dict={},token:Token=None)-> any : 
        return self.sourceManager.eval(operand,context,token)


    def serialize(self,value)-> dict:        
        if isinstance(value,Node):
            return self.nodeManager.serialize(value)
        elif isinstance(value,Operand):
            return self.sourceManager.serialize(value)
        return None      

    def deserialize(self,serialized:dict,type:str='Operand'):
        if type == 'Operand':
            return self.sourceManager.deserialize(serialized)
        elif type == 'Node':
            return self.nodeManager.deserialize(serialized)
        else:
            raise ExpressionError('type: '+type+' not support')           
 
    def vars(self,value)->dict:
        if isinstance(value,Node):
            return self.nodeManager.vars(value)
        elif isinstance(value,Operand):
            return self.sourceManager.vars(value)
        return None       

    def operandType(self,value)->str:
        if isinstance(value,Node):
            return self.nodeManager.operandType(value)
        elif isinstance(value,Operand):
            return self.sourceManager.operandType(value) 
        return None     

    def constants(self,value)->dict:
        if isinstance(value,Node):
            return self.nodeManager.constants(value)
        elif isinstance(value,Operand):
            return self.sourceManager.constants(value)
        return None 
    
    def operators(self,value)->dict:
        if isinstance(value,Node):
            return self.nodeManager.operators(value)
        elif isinstance(value,Operand):
            return self.sourceManager.operators(value)
        return None

    def functions(self,value)->dict:
        if isinstance(value,Node):
            return self.nodeManager.functions(value)
        elif isinstance(value,Operand):
            return self.sourceManager.functions(value)
        return None

class Parser():
    def __init__(self,model):
       self._model = model 
       self.reAlphanumeric = re.compile('[a-zA-Z0-9_.]+$') 
       self.reInt = re.compile('[0-9]+$')
       self.reFloat = re.compile('(\d+(\.\d*)?|\.\d+)([eE]\d+)?')
       self._tripleOperators = []
       self._doubleOperators = [] 
       self._assigmentOperators = []
       self._arrowFunction = []         
   
    def refresh(self):
        for key in self._model.operators.keys():
            if len(key)==2: self._doubleOperators.append(key)
            elif len(key)==3: self._tripleOperators.append(key)

            operator = self._model.operators[key]
            if 2 in operator.keys():
               if operator[2]['category'] == 'assignment':
                  self._assigmentOperators.append(key)

        for key in self._model.functions.keys():
            metadata = self._model.functions[key]
            if metadata['isArrowFunction']: self._arrowFunction.append(key)

    

    @property
    def doubleOperators(self):
        return self._doubleOperators

    @property
    def tripleOperators(self):
        return self._tripleOperators   

    @property
    def arrowFunction(self):
        return self._arrowFunction 

    def priority(self,name:str,cardinality:int)->int:
        try:
            metadata = self._model.getOperatorMetadata(name,cardinality)
            return metadata["priority"] if metadata is not None else -1
        except:
            raise ModelError('error to priority : '+name)   
  
    def isEnum(self,name):    
        return self._model.isEnum(name) 
    def getEnumValue(self,name,option): 
        return self._model.getEnumValue(name,option) 
    def getEnum(self,name): 
        return self._model.getEnum(name) 

        

    def parse(self,expression)->Node:
        try:            
            _parser = _Parser(self,expression)
            node= _parser.parse() 
            del _parser             
            return node  
        except Exception as error:
            raise ExpressionError('expression: '+expression+' error: '+str(error))      
 
class _Parser():
    def __init__(self,mgr:Parser,expression:str):
       self.mgr = mgr 
       self.buffer = list(expression)
       self.length=len(self.buffer)
       self.index=0
    
    def parse(self)->Node:
        nodes=[]
        while not self.end:
            node =self.getExpression(_break=';')
            if node is None:break
            nodes.append(node)
        if len(nodes)==1 :
            return nodes[0]
        return Node('block','block',nodes)

    @property
    def previous(self):
        return self.buffer[self.index-1] 
    @property
    def current(self):
        return self.buffer[self.index]    
    @property
    def next(self):
        return self.buffer[self.index+1]
    @property
    def end(self):
        return self.index >= self.length   

    def getExpression(self,operand1=None,operator=None,_break='')->Node:
        expression = None
        operand2 = None
        isbreak = False               
        while not self.end:
            if operand1 is None and operator is None: 
                operand1=  self.getOperand()
                operator= self.getOperator()
                if operator is None or operator in _break: 
                    expression = operand1
                    isbreak= True
                    break
            operand2=  self.getOperand()
            nextOperator= self.getOperator()
            if nextOperator is None or nextOperator in _break:
                expression= Node(operator,'operator',[operand1,operand2])
                isbreak= True
                break
            elif self.priority(operator)>=self.priority(nextOperator):
                operand1=Node(operator,'operator',[operand1,operand2])
                operator=nextOperator
            else:
                operand2 = self.getExpression(operand1=operand2,operator=nextOperator,_break=_break)
                expression= Node(operator,'operator',[operand1,operand2])
                isbreak= True
                break
        if not isbreak: expression=Node(operator,'operator',[operand1,operand2])
        return expression  
                 

    def getOperand(self)-> Node:        
        isNegative=False
        isNot=False
        isBitNot=False
        operand=None
        char = self.current
        if char == '-':
           isNegative=True
           self.index+=1
           char = self.current
        elif char == '~':
           isBitNot=True
           self.index+=1
           char = self.current            
        elif char == '!':
           isNot=True
           self.index+=1
           char = self.current   

        if char.isalnum():    
            value=  self.getValue()
            if value=='if' and self.current == '(': 
                self.index+=1
                operand = self.getIfBlock()
            elif value=='while' and self.current == '(': 
                self.index+=1
                operand = self.getWhileBlock()            
            elif not self.end and self.current == '(':
                self.index+=1
                if '.' in value:
                    names = value.split('.')
                    name = names.pop()
                    variableName= '.'.join(names)
                    variable = Node(variableName,'variable')
                    operand= self.getChildFunction(name,variable)
                else:
                    args=  self.getArgs(end=')')
                    operand= Node(value,'function',args)                

            elif not self.end and self.current == '[':
                self.index+=1    
                operand = self.getIndexOperand(value)              
            elif self.mgr.reInt.match(value): 
                if isNegative:
                    value = int(value)* -1
                    isNegative= False 
                elif isBitNot:
                    value = ~ int(value)
                    isBitNot= False     
                else:
                    value =int(value)
                operand = Node(value,'constant')
            elif self.mgr.reFloat.match(value):
                if isNegative:
                    value = float(value)* -1
                    isNegative= False
                elif isBitNot:
                    value = ~float(value)
                    isBitNot= False      
                else:
                    value =float(value)
                operand = Node(value,'constant')
            elif value=='true':                
                operand = Node(True,'constant')
            elif value=='false':                
                operand = Node(False,'constant')
            elif self.mgr.isEnum(value):                
                operand= self.getEnum(value)
            else:
                operand = Node(value,'variable')
        elif char == '\'' or char == '"':
            self.index+=1
            result=  self.getString(char)
            operand= Node(result,'constant')
        elif char == '(':
            self.index+=1
            operand=  self.getExpression(_break=')') 
        elif char == '{':
            self.index+=1
            operand = self.getObject()  
        elif char == '[':
            self.index+=1
            elements=  self.getArgs(end=']')
            operand =  Node('array','array',elements)

        if not self.end and  self.current=='.':
            self.index+=1
            name=  self.getValue()
            if self.current == '(': self.index+=1
            operand =self.getChildFunction(name,operand)            

        if isNegative:operand= Node('-','operator',[operand])
        if isNot:operand=Node('!','operator',[operand])
        if isBitNot:operand=Node('~','operator',[operand])  
        return operand

    def priority(self,op:str,cardinality:int=2)->int:
        return self.mgr.priority(op,cardinality)        

    def getValue(self,increment:bool=True):
        buff=[]
        if increment:
            while not self.end and self.mgr.reAlphanumeric.match(self.current):
                buff.append(self.current)
                self.index+=1
        else:
            index = self.index
            while not self.end and self.mgr.reAlphanumeric.match(self.buffer[index]):
                buff.append(self.buffer[index])
                index+=1        
        return ''.join(buff)

    def getOperator(self):
        if self.end:return None 
        op=None
        if self.index+2 < self.length:
            triple = self.current+self.next+self.buffer[self.index+2]
            if triple in self.mgr.tripleOperators :op=triple
            # if triple in ['**=','//=','<<=','>>=']:op=triple
        if op is None and  self.index+1 < self.length:
            double = self.current+self.next
            if double in self.mgr.doubleOperators  :op=double
            # if double in ['**','//','>=','<=','!=','==','+=','-=','*=','/=','%=','&&','||','|=','^=','<<','>>']  :op=double
        if op is None:op=self.current 
        self.index+=len(op)
        return op

    def getString(self,char):
        buff=[]       
        while not self.end :
            if self.current == char:
                if not((self.index+1 < self.length and self.next == char) or (self.previous == char)):
                    break 
            buff.append(self.current)
            self.index+=1
        self.index+=1    
        return ''.join(buff)

    def getArgs(self,end=')'):
        args= []
        while True:
            arg= self.getExpression(_break=','+end)
            if arg is not None:args.append(arg)
            if self.previous==end: break
        return args

    def getObject(self):
        attributes= []
        while True:
            name=None
            if self.current== '"' or  self.current == "'":
                char= self.current
                self.index+=1
                name= self.getString(char)
            else:    
                name= self.getValue()
            if self.current==':':self.index+=1
            else:raise ExpressionError('attribute '+name+' without value')
            value= self.getExpression(_break=',}')
            attribute = Node(name,'keyValue',[value])
            attributes.append(attribute)
            if self.previous=='}':
                break
        
        return  Node('object','object',attributes) 

    def getBlock(self):
        lines= []
        while True:
            line= self.getExpression(_break=';}')
            if line is not None :lines.append(line)
            if self.previous=='}':
                break        
        return Node('block','block',lines)     

    def getIfBlock(self):
        condition= self.getExpression(_break=')')
        if  self.current == '{':
            self.index+=1  
            block= self.getBlock()
        else:
            block= self.getExpression(_break=';') 

        nextValue=self.getValue(increment=False)
        elseblock=None
        if nextValue=='else':
            self.index+=len(nextValue)
            if  self.current == '{':
                self.index+=1  
                elseblock= self.getBlock()
            else:
                elseblock= self.getExpression(_break=';') 

        return Node('if','if',[condition,block,elseblock]) 

    def getWhileBlock(self):
        condition= self.getExpression(_break=')')
        if  self.current == '{':
            self.index+=1  
            block= self.getBlock()
        else:
            block= self.getExpression(_break=';') 

        return Node('while','while',[condition,block])   

    def getChildFunction(self,name,parent):        
        if name in self.mgr.arrowFunction:
            variableName= self.getValue()
            if variableName=='' and self.current==')':
                self.index+=1
                return Node(name,'arrowFunction',[parent]) 
            else:    
                if self.current=='=' and self.next == '>':self.index+=2
                else:raise ExpressionError('map without body')
                variable= Node(variableName,'variable')
                body= self.getExpression(_break=')')
                return Node(name,'arrowFunction',[parent,variable,body])        
        else: 
            args=  self.getArgs(end=')')
            args.insert(0,parent)
            return  Node(name,'childFunction',args)

    def getIndexOperand(self,name):
        idx= self.getExpression(_break=']')
        operand= Node(name,'variable')
        return Node('[]','operator',[operand,idx]) 

    def getEnum(self,value):
        if '.' in value and self.mgr.isEnum(value):
            names = value.split('.')
            enumName = names[0]
            enumOption = names[1] 
            enumValue= self.mgr.getEnumValue(enumName,enumOption)
            return Node(enumValue,'constant')
        else:
            values= self.mgr.getEnum(value)
            attributes= []
            for name in values:
                _value = values[name]
                # _valueType = type(_value).__name__
                attribute = Node(name,'keyValue',[Node(_value,'constant')])
                attributes.append(attribute)
            return Node('object','object',attributes)
   

                            