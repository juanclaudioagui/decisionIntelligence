# The approach is to span all nodes and connections and apply NX library,
# do not trasverse the tree.... then
# example selector

PNAME = ['JH','FAM','BASIC'][1]
SEARCHMODE = ['LIFO','FIFO','METRIC'][0]  # lifo is depth-first, FIFO is breadth,
                                          # METRIC goes for the best node with best metric
SORTMETHOD = ['Metric','MetricReversed','Random'][0]

print ("Solving Puzzle named ",PNAME)
print ( "using Optimized Tree Search with Mode =",SEARCHMODE)
print ( "using sorting method =",SORTMETHOD)

################################################################################
# Transport puzzle algoritm
################################################################################
# The jealous husbands problem, in which
# three married couples must cross a river
# using a boat which can hold  at most two people,
# subject to the constraint that no woman can be in
# the presence of another man unless her husband is also present.

################################################################################
# Disfunctional Family
################################################################################
# We have a dysfunctional family on one side of the river which includes
# mom and 2 daughters, dad and 2 
# Like usual, there is a boat that can hold only two persons at a time
# (dog counts as one person as well).  Obviously, the kids can’t operate
# the boat and we need an adult for that task.

# Rule 1: The Helper  must remain with the dog so she can control it or it will
# head up for a violent biting.
# Rule 2: The dad cannot be left with the daughters without mom
# Rule 3: The mother connot be be left alone with the sons without dad.

################################################################################
# Basic one: Farmer, Wolf, Goat, and Cabbage
################################################################################
# Boat must be operated by the farmer, and at least one element
# If left alone, the Wolf would eat the goat
# if left alone the Goat will eat the cabbage
################################################################################
# import and global variables

import itertools
import time
import os
import networkx as nx
import matplotlib.pyplot as plt
import queue
import random


verbose = True
Right = True
Left  = False 
thePuzzle = None


if PNAME == 'BASIC':                         # Farmer, Wolf, Goat, Cabbage problem
    vizString = ['F','W','G','C','B']
    crewSize  = 4
    target    = 4
    weight    = [1,1,1,1]
    farmer    = 0
    wolf      = 1
    goat      = 2
    cabbage   = 3
    Gfname    = 'BASICGraphViz.pdf'

elif PNAME == 'JH':                           # Jeallous Husband problem
    vizString = ['h1','w1','h2','w2','h3','w3',',B']
    crewSize  = 6
    target    = 6
    weight    = [1,1,1,1,1,1]
    h1      = 0
    w1      = 1
    h2      = 2
    w2      = 3
    h3      = 4
    w3      = 5
    Gfname    = 'JHGraphViz.pdf'
    
elif PNAME == 'FAM':                           # Disfunc Family 
    vizString = ['D','M','S1','S2','D1','D2','H','P',',B']
    crewSize  = 8
    target    = 8
    weight    = [1,1,1,1,1,1,1,1]
    dad       = 0
    mom       = 1
    son1      = 2
    son2      = 3
    girl1     = 4
    girl2     = 5
    help      = 6
    pet       = 7
    Gfname    = 'FAMGraphViz.pdf'

else :
    raise exception("Puzzle "+PNAME+" Not implemented")

print("Libraries loaded")


################################################################################
# Puzzle Classp
################################################################################

class Puzzle:
    thePuzzle = None                                             # Class Variable, rest is global.
    

    def __init__(self, rootState=None):
        self.statesDict= {}                                     # lets use a dict for this...
        self.graph     = nx.Graph(overlap = False)                             # Using networkx
        self.rootState = rootState
        self.endStateColl = []
        self.solPath   = []
        self.paths = []
        self.shortestPath = None
        self.puzzleIsSolved = False
        self.statesQueue = None
   
    @classmethod
    def newPuzzle(self,rootState):
        self.thePuzzle = Puzzle(rootState)
        return self.thePuzzle

#-----------------------------------------------                   
    def start(self,mode):
        Puzzle.thePuzzle = self
        print("Starting Puzzle at node ", self.rootState.printString(),"Mode =",mode)

        # initialize the Q
        if mode == 'FIFO':                                          # makes for breadth
            self.statesQueue = queue.Queue()
        elif mode == 'LIFO':                                        # makes for Depth first
            self.statesQueue = queue.LifoQueue()
        elif mode == 'METRIC':
            self.statesQueue = queue.PriorityQueue()
        else:
             raise exception("Invalid Sorting Method employed: "+mode)
        
        # start with  the root node and go...
        self.qPut(self.rootState)
        self.registerNode(self.rootState)
        
        while self.statesQueue.qsize() != 0:
            node = self.qGet()
            if verbose : print("propagating  node", node.printString(), "Queue size is", self.statesQueue.qsize()+1)
            if Puzzle.thePuzzle.testCompletion(node):
                self.endStateColl.append(node)
                print ("Solution node found, Scanning the rest of the tree" )
                break
            
            node.propagate()
            
        #  build the nx graph
        self.addBranchToGraph(self.rootState)
    
        return
#-----------------------------------------------                   
    def qPut(self, state):
        return self.statesQueue.put((-state.metric(), state))

    def qGet(self):
        return self.statesQueue.get()[1]

        
    def contains(self,state):
        return ( state.short() in self.statesDict )
    
    def stateById(self, stateId):
        if (stateId in self.statesDict): 
            return self.statesDict[stateId]
        else:
            return None
            
#-----------------------------------------------                   
    def registerNode(self, state):

        if (not (state.short() in self.statesDict)):
            self.statesDict[state.short()] = state
            self.addNodeToGraph(state)

            
        return
    
#-Puzzle----------------------------------------------------------------
# we use the move metric to sort the children in the map. 
    def addBranchToGraph(self,state):

        id = lambda state: state.short()
        self.addNodeToGraph(state)
        
        for move in  sorted(state.allMoves(), key = (lambda c: c.metric()), reverse = True):
            if (not (id(move.endState) in self.graph )): self.addBranchToGraph(move.endState)
        
        return
        
#-Puzzle----------------------------------------------------------------
    def addNodeToGraph(self, state):
        
        id = lambda state: state.short()

        G = self.graph
        
        if state.parentState == None:
            G.add_node(id(state))                                             # stand alone
        else:
            label = state.parentState.moveToEndState(state).printString()
            G.add_edge(id(state.parentState),id(state),label=label)           # hanging
        
        for child in state.children():
            G.add_edge(id(state), id(child))
    
            
        return

#-Puzzle -----------------------------------------------------------------
    def analyzeGraph(self):
        # look for nodes matching target state
        thePuzzle.endStateColl = [s for s in filter( lambda aState : (aState.metric() == target ),thePuzzle.statesDict.values())]    
        print ("Found ", len(thePuzzle.endStateColl), "nodes with the Puzzle target metric")
        
        # compute all paths 
        for s in thePuzzle.endStateColl:
            self.paths.append([p for p in nx.all_simple_paths(self.graph, source=self.rootState.short(), target=s.short())])        
            self.shortestPath = nx.shortest_path(self.graph, source=self.rootState.short(), target=s.short(), weight=None, method='dijkstra')
        
        print ( "shortest path in Graph, length =", len(self.shortestPath))
        for i,aN  in zip(range(len(self.shortestPath)),self.shortestPath): print (self.shortestPath[i])
        return
    
#-Puzzle----------------------------------------
    def plot(self):
    #  plots the entire tree, using pygraphviz, using format

        id       = lambda state: state.short()
        nodeByID = lambda id: self.statesDict[id]

        aPlot = nx.nx_agraph.to_agraph(self.graph)
        
        # shade end nodes in gray
        # for node in Puzzle.thePuzzle.statesDict.values():
        #     if len(node.children()) == 0 :
        #         aPlot.get_node(id(node)).attr["style"] = "filled"
        #         aPlot.get_node(id(node)).attr["fillcolor"]= 'gray'        
        
        # Plot the found  path in green
        for inode, node  in zip(range(len(self.solPath)-1),self.solPath[:-1]):
            node = aPlot.get_node(id(node))
            node.attr["style"] = "filled"
            node.attr["fillcolor"] = "yellow"

            edge = aPlot.get_edge(id(self.solPath[inode]),id(self.solPath[inode+1]))
            edge.attr["style"] = "dashed"
            edge.attr["color"] = "green"

            node = aPlot.get_node(id(self.rootState))
            node.attr["style"] = "filled"
            node.attr["fillcolor"] = "green"

        for node in self.endStateColl:
            node = aPlot.get_node(id(node))
            node.attr["style"] = "filled"
            node.attr["fillcolor"] = "red"
            
            
        
        
        aPlot.layout(prog="dot")
        if PNAME == 'FAM':
            fname = 'FAMTreeGraph.pdf'
        elif PNAME == 'JH':
            fname = 'JHTreeGraph.pdf'
        elif PNAME == 'BASIC':
            fname = 'BASICTreeGraph.pdf'
        else:
            raise exception('Wrong Puzzle name specified')

        aPlot.draw(fname)
        
        return

#-Puzzle----------------------------------------
    def testCompletion(self, state):
        # this is the time to verify completion of the Puzzle

        
        if verbose: print ("testing Node ", state.printString(), "metric = ",state.metric())
        if  ( state.metric() == target):

            print ("Target reached node",state.short()," Current Nodes in tree ", len(self.statesDict.values()),"backtracking")

            node = state
            path =[node]
            while node.parentState != None :
                node = node.parentState
                path.append(node)

            # reverse the path
            Puzzle.thePuzzle.solPath = [ node for node in reversed(path) ]
            
            # print out from the root down
            path = Puzzle.thePuzzle.solPath
            for i,node in zip(range(len(path)-1), path[:-1]):
                print ( "Node",i,node.printString(), "metric:", node.metric(), "Move: ",node.moveToEndState(path[i+1]).printString())

            print ( "Node",len(path),path[-1].printString(), "metric:", path[-1].metric())
            return True

        else:
            return False

################################################################################
# Move Class
# data is a left/right for all elements, including the boat as the last element
################################################################################

class Move:
    def __init__(self, data, sense,initState=None,endState=None):
        self.data = data
        self.sense = sense
        self.initState = initState
        self.endState = endState

#-----------------------------------------------
    def short(self):
        short = ''
        for a in self.data: 
            if a : short += 'R'
            else : short += 'L'
        if self.sense:
            short += ' >R'
        else:
            short += ' L<'
            
        return short

#- Move -------------------------------------
    def metric(self):
        metric = 0
        for val, iCrew in zip (weight, self.data):  
            if iCrew  != None: metric += val
        
        if not self.sense: metric *= -1 
        return  metric

#-----------------------------------------------
    def printString(self):
        short = ''
        for i,crew in zip(range(crewSize),self.data):
            if crew :
                short  += vizString[i]+' '

        if self.sense:
            short ='(' + short + '>R)'
        else:
            short = '(L<' + short + ')'
            
        return short

#Move Class Rewrite in each case  ----------------            
    @classmethod
    def isValidMove(self, moveData):
        # this must be rewritten for each case.....
        # it must apply the specific games rule

        if PNAME == 'JH':
            #Jeallous Husband Move rules------------------------------------------------    
            # rule 1: The ferry can carry no more than 2 people.
            rule1 = sum(filter( lambda i: i !=None , moveData))  in [1,2]          
            return rule1
        
        elif PNAME == 'FAM':
            # Disfunctional family moves rule ------------------------------------------
            # there is one rule for the move
            rule1 = sum(filter( lambda i: i !=None , moveData))  in [1,2]                                     # The ferry can carry no more than 2 people.
            rule2 = sum(filter( lambda i: i !=None , [moveData[dad],moveData[mom],moveData[help]])) in [1,2]  # the Ferry must be operated by an adult
            return (rule1 and rule2)

        elif PNAME == 'BASIC':
            # Wolf Goat, Cabbage  Moves ----------------------------------------------------
            # the rules are that the 
            # rule 1: The move includes the farmer and only one other item....
            rule1 =  moveData[farmer] == True                                       # Farmer is on boat
            rule2 =  sum(filter( lambda i: i !=None , moveData[1:])) <= 1           # only one other item in boat
            return (rule1 and rule2)

        else:
            raise exception("Puzzle "+PNAME+" Not implemented")
            


################################################################################
# State Class
################################################################################

class State:                      
    def __init__(self,data,parentState=None):       
        self.data        = data
        self.parentState = None
        self.moves       = None
        self.parentState = parentState
        self.isTarget    = None
        self.propagated  = False
        

#--------------------------------------------------------------------        
    @classmethod
    def newValidState(self, data, parentState=None):  
        if self.isValidStateData(data):
            return State(data,parentState)
        else:
            raise exception("Invalid Data for State creation")
            
    @classmethod
    def newOrExistingState(self, data, parentState=None):
        stateId = State(data).short()
        state = Puzzle.thePuzzle.stateById(stateId)
        if state is None:
            return State.newValidState(data, parentState)
        else:
            return state

#-----------------------------------------------               
    def __lt__(self, state2):
        return self.metric() < state2.metric()
    
#-----------------------------------------------               
    def short(self):
        leftShore = ''
        rightShore = ''
        for i,pos in zip(range(crewSize+1),self.data):
            if pos:
                rightShore += vizString[i]
            else:
                leftShore  += vizString[i]
        
        return '['+leftShore + '|'+rightShore+']'
    
#-----------------------------------------------               
    def printString(self):
        leftShore = ''
        rightShore = ''
        for i,pos in zip(range(crewSize+1),self.data):
            if pos:
                rightShore += vizString[i]
                leftShore += '  '
            else:
                rightShore += '  '
                leftShore  += vizString[i]
        short =  'M:'+str(self.metric()) +' C:'+str(self.childrenCount())

        return '['+leftShore + ' | - | '+rightShore+']'+short

    
#-----------------------------------------------               
    def children(self):
        if self.moves == None:
            return []
        else:
            return [ move.endState for move in self.moves ]        

#-----------------------------------------------               
    def childrenCount(self):
        return len(self.children())

#-State----------------------------------------------[Consider if this method needs to be rewritten]
    def metric(self):
        metric = 0
        for loc,val in zip (weight, self.data[:len(weight)]): metric += loc*val
        return metric

#-State----------------------------------------------               
    def propagate(self):
            
        if self.propagated == True : return
         
        
        if verbose : print ("Propagating node ",self.printString(), "Prop State = ",self.propagated)
        # this first call gives me moves which are valid at the current state
        self.allMoves()

        # computes and populates the endState
        for aMove in self.allMoves():  aMove.endState= self.applyMove(aMove)

        # Retain only the valid endState which are not Null
        toRetain = lambda aMove: ( aMove.endState != None )
        self.moves = [m for m in filter(lambda aMove: toRetain(aMove),self.moves)]

        # now lets a list of children properly ordered
        if   SORTMETHOD == 'Metric':
            childrenList =  sorted(self.children(), key = (lambda c: c.metric()), reverse = True)              
        elif SORTMETHOD == 'MetricReversed':
            childrenList =  sorted(self.children(), key = (lambda c: c.metric()), reverse = False)              
        elif SORTMETHOD == 'Random':
            childrenList =  sorted(self.children(), key = (lambda _: random.random()))
        else :
            childrenList = self.children()

        for child in childrenList:
            Puzzle.thePuzzle.registerNode(child)
            Puzzle.thePuzzle.qPut(child)
                
        self.propagated = True

        return

#-State----------------------------------------------                   
    def allMoves(self):
    # if moves = None, then computes and populates the list of all possible nodes
    # returns the list of all possible moves, for a given state\
    # fijar el sense contrario al del boatLoc del init (1)
    # para cada uno de la crew, fijar el contrario a su estado o no ( 2^ ncrew opciones)
    # filtrar eliminando las que no cumplen las condiciones de peso o skill

        if self.moves == None:
        
            sense = (not self.data[-1])
            list = []
            for iCrew in range(crewSize):
                if self.data[iCrew] != sense:
                    list.append((None,True))
                else:
                    list.append((None,))
                
            allMovesData = [p for p in itertools.product(*list)]

            allValidMovesData = [ d for d  in filter(lambda aD: Move.isValidMove(aD),allMovesData)]
        
            if verbose: print ("@Moves: ",len(allMovesData), "o/w", len(allValidMovesData)," are valid moves")
            self.moves =  [ Move(data,sense,initState=self) for data in allValidMovesData ]

        return self.moves
            
# State----------------------------------------------        
    def applyMove(self, aMove):
    # computes the end state, applying the move to self, Null if not applicable)
    # for an init state, left/Right, boatLoc, applies the move
    # for all the True, set them to the boatSense, then appy boatLoc = boatSense
    # see if there is any state already created, if so link to it. other wise create, link and append.p    

        # applies sense of the move to the elements which are moved True
        newStateData = self.data.copy() # deep copy...

        for i in range(crewSize):
            if aMove.data[i]: newStateData[i] = aMove.sense
        newStateData[crewSize] = aMove.sense

        # if the endState is valid, the create the end state and return  it
        if State.isValidStateData(newStateData):
            return State.newOrExistingState(newStateData,parentState=self)
        else:
            return None

# State -------------------------
    # returns the movement that leads from self to the endState given
    def moveToEndState(self,endState):
        try:
            return self.moves[self.children().index(endState)]
        except:
            print ("EndState not registered ?",endState.printString())

               
#- State----------------------------------------------REWRITE >>>>>>>>>>>>>>               
    @classmethod
    def isValidStateData(self, d):
        # this must be rewritten for each case.....
        # it must apply the specific games rule
       
    
        #- Jeallous Husbands State Rules-----------------------------------------------------------        
        if PNAME == 'JH':
            #rule subject to the constraint  no woman can be in the presence of another man
            # unless her husband is also present
            husbands = [ d[i] for i in range(0,crewSize,2 )]
            wives    = [ d[i] for i in range(1,crewSize,2 )]
            # if the husband is not with wive then    no husband is present at wife side..
            rule = True
            for iWive in range(0,len(wives)):
                if (wives[iWive] != husbands[iWive]):  
                    val = sum(list(map(lambda aH:(aH ==wives[iWive]),husbands)))
                    if (val != 0): return False
            return  True

#- disfunctional Family State rules -----------------------------------------------------    
        elif PNAME == 'FAM':
            # rule 1   Dad can not be in the presence of the girls w/out Mom  
            if (d[dad] == d[girl1]) or (d[dad] == d[girl2]):      
                rule1  = (d[dad] == d[mom])
            else:     
                rule1 = True
                
            #rule 2   Mom can not be in the presence of the boys w/out Dad   
            if (d[mom] == d[son1]) or (d[mom] == d[son2]):      
                rule2  = (d[dad] == d[mom])
            else:
                rule2 = True
        
            #rule 3   The pet can not be alone with any of the family w/out the helpert.
            if (sum(d[:6]) == 1) or (sum(d[:6]) == 5):
                rule3 = (d[help] == d[pet])
            else:
                rule3 = True

            return  (rule1 and rule2 and rule3)
# Wolf, Goat, Cabbage  State rules--------------------------------------------------------
        elif PNAME == 'BASIC':
            # Rule 1 with no Farmer, the wolf would eat the goat,
            rule1 = not ((d[wolf] == d[goat]) and d[wolf] != d[farmer])
        
            # Rule 2 With no Farmern the goat would eat the cabbage. 
            rule2 = not ((d[cabbage] == d[goat]) and d[cabbage] != d[farmer])
            return (rule1 and rule2)

        else:
            raise exception("Puzzle "+PNAME+" Not implemented")            


################################################################################
# Execute Section
################################################################################
    
try:
    # all starting at left side of the river
    rootState = State.newValidState( [Left]*(crewSize+1))
    thePuzzle = Puzzle.newPuzzle(rootState=rootState)
    t0 = time.perf_counter()
    thePuzzle.start(mode = SEARCHMODE)
    print ("Done scanning tree", len(Puzzle.thePuzzle.statesDict.values()),"Nodes found")
finally:
    t1 = time.perf_counter()
    Puzzle.thePuzzle.plot()
    print('Time = ',t1-t0, ' Nodes = ', len(thePuzzle.statesDict.values()))


# thePuzzle.paths
