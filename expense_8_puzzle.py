import sys
import heapq
import datetime



class Expense_Puzzle:
    
    '''
    Initializing the Expense Puzzle node to store required data and to 
    instantiate the values needed to be printed in the end for the users.
    '''
    def __init__(self, puzzle_start, puzzle_goal):
        self.puzzle_start = puzzle_start
        self.puzzle_goal = puzzle_goal
        self.nodes_popped = 0
        self.nodes_expanded = 0
        self.nodes_generated = 0
        self.max_fringe_size = 0


    '''
    Figuring out the legal moves that can be made in the puzzle such that we 
    don't go out of bounds and that we find the right empty space to move the 
    items in the puzzle.
    '''
    def possible_moves(self, state):
        zeros = [(i, j) for i in range(3) for j in range(3) if state[i][j] == 0]
        x, y = next(iter(zeros))
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        valid_moves = []
        for i, j in moves:
            if 0 <= x + i < 3 and 0 <= y + j < 3:
                new_state = [row.copy() for row in state]
                new_state[x][y], new_state[x+i][y+j] = new_state[x+i][y+j], new_state[x][y]
                valid_moves.append(new_state)
        return valid_moves

    '''
    As the output of the program requires to show the steps involved in acheiveing
    the goal state of the puzzle, we will grab that information and return it
    along with the final cost.
    '''
    def get_output(self, states):
        total_cost = 0
        steps = []
        for state in states:
            for x in range(3):
                for y in range(3):
                    if state[x][y] < 0:
                        value = abs(state[x][y])
                        steps.extend([f"Move {value} {self.choose_direction(x, y, i, j)}"
                                       for i in range(3) for j in range(3)
                                       if state[i][j] > 0])
                        total_cost += value

        return total_cost, steps

    '''
    This is a helper function used to figure out what step is taken in the puzzle
    to store in the history of steps.
    '''
    def choose_direction(self, x, y, i, j):
        if x == i:
            return 'Left' if j > y else 'Right'
        if y == j:
            return 'Up' if i > x else 'Down'
        return None

    '''
    Creating a heuristic to use for the A* and Greedy methods to adjust in the 
    calculations of the cost.
    '''
    def heuristic(self,start, goal):
        value = 0
        for a, row in enumerate(start):
            for b, element in enumerate(row):
                if element != goal[a][b]:
                    x, y = next(((i, j) for i, r in enumerate(goal) for j, e in enumerate(r) if e == element), (None, None))
                    if (x, y) != (None, None):
                        value += (abs(x - a) + abs(y - b)) * element
        return value
    
    
    def greedy(self, search_trace=False):
        self.nodes_generated += 1
        trace_filename  = ""
        '''
        Setting up the search trace dump file with its unique naming for further
        use later on.
        '''
        if search_trace:
            time = datetime.datetime.now()
            file_time = time.strftime('%Y%m%d-%H%M%S')
            trace_filename = f"trace-{file_time}.txt"
            trace_file = open(trace_filename, 'w')
            trace_file.write("Greedy Algorithm \n")
        
        '''
        Initializing the fringe contents with the fringe properties and also
        initialzing closed states to not explore previous states again.
        '''
        fringe = []
        heapq.heappush(fringe,((self.heuristic(self.puzzle_start, self.puzzle_goal), self.puzzle_start, [self.puzzle_start], 0)))
        state_closed = {}

        while fringe:
            '''
            Will be getting the contents of the fringe out and assign it to its
            respective variables to use later.
            '''
            fringe_contents = (heapq.heappop(fringe))
            fringe_state, fringe_history, fringe_cost = fringe_contents[1:]
            self.nodes_popped += 1
            state_closed[str(fringe_state)] = 1
            possible_moves = self.possible_moves(fringe_state)
            
            '''
            Printing to the search trace file so we can keep track of our steps
            to debug if neccesary and to just view if needed.
            '''
            if search_trace:
                trace_file.write("------------------------\n")
                trace_file.write(f"Fringe:\n{list(fringe)}\n")
                trace_file.write(f"Closed States :\n{state_closed}\n")
                trace_file.write(f"Nodes Expanded: {self.nodes_expanded}\n")
                trace_file.write(f"Nodes Popped: {self.nodes_popped}\n")
                trace_file.write(f"Nodes Generated: {self.nodes_generated}\n")
            
            '''
            Checking if each state based on possible moves that can happen
            in the puzzle have been performed before and if not, we will add that 
            to our history so we can backtrack later.
            We will also be updating the required puzzle properties.
            '''
            for i in range(len(possible_moves)):
                self.nodes_expanded += 1
                if not state_closed.get(str(possible_moves[i])):
                    total_cost = self.heuristic(possible_moves[i], self.puzzle_goal)
                    heapq.heappush(fringe,((total_cost, possible_moves[i], fringe_history + [possible_moves[i]], fringe_cost + 1)))
                    self.nodes_generated += 1
                    self.max_fringe_size = len(fringe) if self.max_fringe_size < len(fringe) else self.max_fringe_size
            
            '''
            Check if the fringe state matches the state of the goal that
            was given to us, and if so we will get the history of steps taken 
            to reach here and return that so users can receive their output.
            '''
            if fringe_state == self.puzzle_goal:
                states = [[[(fringe_history[i][x][y] - fringe_history[i+1][x][y]) for y in range(3)] 
                         for x in range(3)] for i in range(len(fringe_history)-1)]
                final_cost, steps = self.get_output(states)
                if search_trace:
                    trace_file.write(f"Solution Found at depth {len(steps)} with cost of {final_cost}.")
                    trace_file.close()
                return trace_filename,steps, final_cost

        return None, None, None 
        
    def a_star(self, search_trace=False):
        self.nodes_generated += 1
        trace_filename  = ""
        '''
        Setting up the search trace dump file with its unique naming for further
        use later on.
        '''
        if search_trace:
            time = datetime.datetime.now()
            file_time = time.strftime('%Y%m%d-%H%M%S')
            trace_filename = f"trace-{file_time}.txt"
            trace_file = open(trace_filename, 'w')
            trace_file.write("A Star Algorithm \n")
        
        '''
        Initializing the fringe contents with the fringe properties and also
        initialzing closed states to not explore previous states again.
        '''
        fringe = []
        heapq.heappush(fringe,((self.heuristic(self.puzzle_start, self.puzzle_goal), self.puzzle_start, [self.puzzle_start], 0)))
        state_closed = {}
        
        while fringe:
            '''
            Will be getting the contents of the fringe out and assign it to its
            respective variables to use later.
            '''
            fringe_contents = heapq.heappop(fringe)
            fringe_state, fringe_history, fringe_cost = fringe_contents[1:]
            self.nodes_popped += 1
            state_closed[str(fringe_state)] = 1
            possible_moves = self.possible_moves(fringe_state)
            
            '''
            Printing to the search trace file so we can keep track of our steps
            to debug if neccesary and to just view if needed.
            '''
            if search_trace:
                trace_file.write("------------------------\n")
                trace_file.write(f"Fringe:\n{list(fringe)}\n")
                trace_file.write(f"Closed States :\n{state_closed}\n")
                trace_file.write(f"Nodes Expanded: {self.nodes_expanded}\n")
                trace_file.write(f"Nodes Popped: {self.nodes_popped}\n")
                trace_file.write(f"Nodes Generated: {self.nodes_generated}\n")
            
            
            '''
            Checking if each state based on possible moves that can happen
            in the puzzle have been performed before and if not, we will add that 
            to our history so we can backtrack later.
            We will also be updating the required puzzle properties.
            '''
            for i in range(len(possible_moves)):
                self.nodes_expanded += 1
                if not state_closed.get(str(possible_moves[i])):
                    total_cost = fringe_cost + 1 + self.heuristic(possible_moves[i], self.puzzle_goal)
                    heapq.heappush(fringe,((total_cost, possible_moves[i], fringe_history + [possible_moves[i]], fringe_cost + 1)))
                    self.nodes_generated += 1
                    self.max_fringe_size = len(fringe) if self.max_fringe_size < len(fringe) else self.max_fringe_size

            '''
            Check if the fringe state matches the state of the goal that
            was given to us, and if so we will get the history of steps taken 
            to reach here and return that so users can receive their output.
            '''        
            if fringe_state == self.puzzle_goal:
                states = [[[(fringe_history[i][x][y] - fringe_history[i+1][x][y]) for y in range(3)] 
                         for x in range(3)] for i in range(len(fringe_history)-1)]
                
                final_cost, steps = self.get_output(states)
                if search_trace:
                    trace_file.write(f"Solution Found at depth {len(steps)} with cost of {final_cost}.")
                    trace_file.close()
        
                return trace_filename,steps, final_cost

        return None, None, None 
    
    def bfs(self, search_trace=False):
        self.nodes_generated += 1
        trace_filename  = ""
        '''
        Setting up the search trace dump file with its unique naming for further
        use later on.
        '''
        if search_trace:
            time = datetime.datetime.now()
            file_time = time.strftime('%Y%m%d-%H%M%S')
            trace_filename = f"trace-{file_time}.txt"
            trace_file = open(trace_filename, 'w')
            trace_file.write("BFS Algorithm \n")
        
        '''
        Initializing the fringe contents with the fringe properties and also
        initialzing closed states to not explore previous states again.
        '''
        fringe = []
        fringe.append((self.puzzle_start, [self.puzzle_start]))
        state_closed = {}
        
        while fringe:
            '''
            Will be getting the contents of the fringe out and assign it to its
            respective variables to use later.
            '''
            fringe_contents = fringe.pop(0)
            fringe_state,fringe_history = fringe_contents[0:]
            self.nodes_popped += 1
            state_closed[str(fringe_state)] = 1
            possible_moves = self.possible_moves(fringe_state)
            
            '''
            Printing to the search trace file so we can keep track of our steps
            to debug if neccesary and to just view if needed.
            '''
            if search_trace:
                trace_file.write("------------------------\n")
                trace_file.write(f"Fringe:\n{list(fringe)}\n")
                trace_file.write(f"Closed States :\n{state_closed}\n")
                trace_file.write(f"Nodes Expanded: {self.nodes_expanded}\n")
                trace_file.write(f"Nodes Popped: {self.nodes_popped}\n")
                trace_file.write(f"Nodes Generated: {self.nodes_generated}\n")
            
            '''
            Checking if each state based on possible moves that can happen
            in the puzzle have been performed before and if not, we will add that 
            to our history so we can backtrack later.
            We will also be updating the required puzzle properties.
            '''
            for i in range(len(possible_moves)):
                self.nodes_expanded += 1
                if not state_closed.get(str(possible_moves[i])):
                    fringe.append((possible_moves[i], fringe_history + [possible_moves[i]]))
                    self.nodes_generated += 1
                    self.max_fringe_size = len(fringe) if self.max_fringe_size < len(fringe) else self.max_fringe_size

                        
            '''
            Check if the fringe state matches the state of the goal that
            was given to us, and if so we will get the history of steps taken 
            to reach here and return that so users can receive their output.
            '''            
            if fringe_state == self.puzzle_goal:
                states = [[[(fringe_history[i][x][y] - fringe_history[i+1][x][y]) for y in range(3)] 
                         for x in range(3)] for i in range(len(fringe_history)-1)]
                final_cost, steps = self.get_output(states)
                if search_trace:
                    trace_file.write(f"Solution Found at depth {len(steps)} with cost of {final_cost}.")
                    trace_file.close()
                return trace_filename, steps, final_cost
            
        return None, None, None 
    
    
    def ucs(self, search_trace=False):
        self.nodes_generated += 1
        trace_filename  = ""
        '''
        Setting up the search trace dump file with its unique naming for further
        use later on.
        '''
        if search_trace:
            time = datetime.datetime.now()
            file_time = time.strftime('%Y%m%d-%H%M%S')
            trace_filename = f"trace-{file_time}.txt"
            trace_file = open(trace_filename, 'w')
            trace_file.write("UCS Algorithm \n")
        
        '''
        Initializing the fringe contents with the fringe properties and also
        initialzing closed states to not explore previous states again.
        '''
        fringe = []
        heapq.heappush(fringe,((0, self.puzzle_start, [self.puzzle_start], 0)))
        state_closed = {}

        while fringe:
            '''
            Will be getting the contents of the fringe out and assign it to its
            respective variables to use later.
            '''
            fringe_contents = heapq.heappop(fringe)
            fringe_state, fringe_history, fringe_cost = fringe_contents[1:]

            self.nodes_popped += 1
            state_closed[str(fringe_state)] = 1
            possible_moves = self.possible_moves(fringe_state)
            
            '''
            Printing to the search trace file so we can keep track of our steps
            to debug if neccesary and to just view if needed.
            '''
            if search_trace:
                trace_file.write("------------------------\n")
                trace_file.write(f"Fringe:\n{list(fringe)}\n")
                trace_file.write(f"Closed States :\n{state_closed}\n")
                trace_file.write(f"Nodes Expanded: {self.nodes_expanded}\n")
                trace_file.write(f"Nodes Popped: {self.nodes_popped}\n")
                trace_file.write(f"Nodes Generated: {self.nodes_generated}\n")

            '''
            Checking if each state based on possible moves that can happen
            in the puzzle have been performed before and if not, we will add that 
            to our history so we can backtrack later.
            We will also be updating the required puzzle properties.
            '''
            for i in range(len(possible_moves)):
                self.nodes_expanded += 1
                if not state_closed.get(str(possible_moves[i])):
                    total_cost = fringe_cost + 1
                    heapq.heappush(fringe,((total_cost, possible_moves[i], fringe_history + [possible_moves[i]], fringe_cost + 1)))
                    self.nodes_generated += 1
                    self.max_fringe_size = len(fringe) if self.max_fringe_size < len(fringe) else self.max_fringe_size

                        
            '''
            Check if the fringe state matches the state of the goal that
            was given to us, and if so we will get the history of steps taken 
            to reach here and return that so users can receive their output.
            '''          
            if fringe_state == self.puzzle_goal:
                states = [[[(fringe_history[i][x][y] - fringe_history[i+1][x][y]) for y in range(3)] 
                         for x in range(3)] for i in range(len(fringe_history)-1)]
                final_cost, steps = self.get_output(states)
                if search_trace:
                    trace_file.write(f"Solution Found at depth {len(steps)} with cost of {final_cost}.")
                    trace_file.close()
                return trace_filename, steps, final_cost

        return None, None, None 
    
    def dfs(self, search_trace=False):
        self.nodes_generated += 1
        '''
        Initializing the fringe contents with the fringe properties and also
        initialzing closed states to not explore previous states again.
        Also getting the search trace buffer set up for later processing.
        '''
        trace_buffer =  []
        if search_trace:
            trace_buffer.append("DFS Algorithm \n")
        fringe = []
        fringe.append((self.puzzle_start, [self.puzzle_start]))
        state_closed = {}
        counter = 0
        
        while fringe:
            '''
            Will be getting the contents of the fringe out and assign it to its
            respective variables to use later.
            '''
            fringe_contents = fringe.pop()
            fringe_state,fringe_history = fringe_contents[0:]
        
            self.nodes_popped += 1
            state_closed[str(fringe_state)] = 1
            possible_moves = self.possible_moves(fringe_state)
            
            '''
            Setting up the search trace dump file buffer so that the search trace 
            can be added to this and later printed as this will be more efficient
            method since this algorithm will take a lot of time.
            Keeping the count to 50 to limit amount of printing and to be faster.
            '''
            if search_trace and counter <= 50:
                trace_buffer.append("------------------------\n")
                trace_buffer.append(f"Fringe:\n{list(fringe)}\n")
                trace_buffer.append(f"Closed States :\n{state_closed}\n")
                trace_buffer.append(f"Nodes Expanded: {self.nodes_expanded}\n")
                trace_buffer.append(f"Nodes Popped: {self.nodes_popped}\n")
                trace_buffer.append(f"Nodes Generated: {self.nodes_generated}\n")
                
            '''
            Checking if each state based on possible moves that can happen
            in the puzzle have been performed before and if not, we will add that 
            to our history so we can backtrack later.
            We will also be updating the required puzzle properties.
            '''
            for i in range(len(possible_moves)):
                self.nodes_expanded += 1
                if not state_closed.get(str(possible_moves[i])):
                    fringe.append((possible_moves[i], fringe_history + [possible_moves[i]]))
                    self.nodes_generated += 1
                    self.max_fringe_size = len(fringe) if self.max_fringe_size < len(fringe) else self.max_fringe_size

            
            '''
            Check if the fringe state matches the state of the goal that
            was given to us, and if so we will get the history of steps taken 
            to reach here and return that so users can receive their output.
            '''         
            if fringe_state == self.puzzle_goal:
                states = [[[(fringe_history[i][x][y] - fringe_history[i+1][x][y]) for y in range(3)] 
                         for x in range(3)] for i in range(len(fringe_history)-1)]
                final_cost, steps = self.get_output(states)
                if search_trace and counter <= 50:
                    trace_buffer.append(f"Solution Found at depth {len(steps)} with cost of {final_cost}.")
                return trace_buffer, steps, final_cost
            counter += 1
            
        return None, None, None 
    
    def dls(self, limit, search_trace=False):
        self.nodes_generated += 1
        '''
        Initializing the fringe contents with the fringe properties and also
        initialzing closed states to not explore previous states again.
        Also getting the search trace buffer set up for later processing.
        '''
        trace_buffer = []
        if search_trace:
            trace_buffer.append("DLS Algorithm \n")
        fringe = []
        fringe.append((self.puzzle_start, [self.puzzle_start],0))
        state_closed = {}
    
        while fringe:
            '''
            Will be getting the contents of the fringe out and assign it to its
            respective variables to use later.
            '''
            fringe_contents = fringe.pop()
            fringe_state,fringe_history,fringe_depth = fringe_contents[0:]
            
            self.nodes_popped += 1
            
            '''
            Making sure depth stays within limits
            '''
            if fringe_depth <= limit:
                possible_moves = self.possible_moves(fringe_state)
                '''
                Setting up the search trace dump file buffer so that the search trace 
                can be added to this and later printed as this will be more efficient
                method since this algorithm will take a lot of time.
                Keeping the count to 50 to limit amount of printing and to be faster.
                '''
                if search_trace:
                    trace_buffer.append("------------------------\n")
                    trace_buffer.append(f"Fringe:\n{list(fringe)}\n")
                    trace_buffer.append(f"Closed States :\n{state_closed}\n")
                    trace_buffer.append(f"Nodes Expanded: {self.nodes_expanded}\n")
                    trace_buffer.append(f"Nodes Popped: {self.nodes_popped}\n")
                    trace_buffer.append(f"Nodes Generated: {self.nodes_generated}\n")
                
                '''
                Checking if each state based on possible moves that can happen
                in the puzzle have been performed before and if not, we will add that 
                to our history so we can backtrack later.
                We will also be updating the required puzzle properties.
                '''    
                for i in range(len(possible_moves)):
                    self.nodes_expanded += 1
                    if not state_closed.get(str(possible_moves[i])):
                        fringe.append((possible_moves[i], fringe_history + [possible_moves[i]],fringe_depth+1))
                        self.nodes_generated += 1
                        self.max_fringe_size = len(fringe) if self.max_fringe_size < len(fringe) else self.max_fringe_size

            '''
            Check if the fringe state matches the state of the goal that
            was given to us, and if so we will get the history of steps taken 
            to reach here and return that so users can receive their output.
            '''    
            if fringe_state == self.puzzle_goal:
                states = [[[(fringe_history[i][x][y] - fringe_history[i+1][x][y]) for y in range(3)] 
                         for x in range(3)] for i in range(len(fringe_history)-1)]
                final_cost, steps = self.get_output(states)
                if search_trace:
                    trace_buffer.append(f"Solution Found at depth {len(steps)} with cost of {final_cost}.")
                return trace_buffer,steps, final_cost
            
            
        return None,None, None 
    
    
    def ids(self,search_trace=False):
        '''
        Getting the search trace buffer set up for later processing.
        Intializing depth at zero to start process.
        '''
        trace_buffer =  []
        if search_trace:
            trace_buffer.append("IDS Algorithm \n")
        depth = 0
        
        while True:
            self.nodes_generated += 1
            '''
            Initializing the fringe contents with the fringe properties and also
            initialzing closed states to not explore previous states again.
            '''
            fringe = []
            fringe.append((self.puzzle_start, [self.puzzle_start],0))
            state_closed = {}
            
            while fringe:
                '''
                Will be getting the contents of the fringe out and assign it to its
                respective variables to use later.
                '''
                fringe_contents = fringe.pop()
                fringe_state,fringe_history,fringe_depth = fringe_contents[0:]
                
                self.nodes_popped += 1
                '''
                Setting up the search trace dump file buffer so that the search trace 
                can be added to this and later printed as this will be more efficient
                method since this algorithm will take a lot of time.
                Keeping the count to 50 to limit amount of printing and to be faster.
                '''
                if search_trace:
                    trace_buffer.append("------------------------\n")
                    trace_buffer.append(f"Fringe:\n{list(fringe)}\n")
                    trace_buffer.append(f"Closed States :\n{state_closed}\n")
                    trace_buffer.append(f"Nodes Expanded: {self.nodes_expanded}\n")
                    trace_buffer.append(f"Nodes Popped: {self.nodes_popped}\n")
                    trace_buffer.append(f"Nodes Generated: {self.nodes_generated}\n")
                
                '''
                Making sure depth stays within limits
                '''
                if fringe_depth <= depth:
                    possible_moves = self.possible_moves(fringe_state)
                    '''
                    Checking if each state based on possible moves that can happen
                    in the puzzle have been performed before and if not, we will add that 
                    to our history so we can backtrack later.
                    We will also be updating the required puzzle properties.
                    '''    
                    for i in range(len(possible_moves)):
                        self.nodes_expanded += 1
                        if not state_closed.get(str(possible_moves[i])):
                            fringe.append((possible_moves[i], fringe_history + [possible_moves[i]],fringe_depth+1))
                            self.nodes_generated += 1
                            self.max_fringe_size = len(fringe) if self.max_fringe_size < len(fringe) else self.max_fringe_size
                
                '''
                Check if the fringe state matches the state of the goal that
                was given to us, and if so we will get the history of steps taken 
                to reach here and return that so users can receive their output.
                ''' 
                if fringe_state == self.puzzle_goal:
                    states = [[[(fringe_history[i][x][y] - fringe_history[i+1][x][y]) for y in range(3)] 
                             for x in range(3)] for i in range(len(fringe_history)-1)]
                    final_cost, steps = self.get_output(states)
                    if search_trace:
                        trace_buffer.append(f"Solution Found at depth {len(steps)} with cost of {final_cost}.")
                    return trace_buffer,steps, final_cost
             
            depth += 1  
            
        return None, None, None 
        
if __name__ == "__main__":
    
    '''
    Setting up the variables based on command line arguments and checking what
    parameters are given to adjust behavior of the search trace dump.
    '''
    algorithm = "a_star"
    dump_flag = "false"
    start_file, goal_file = sys.argv[1],sys.argv[2]
    
    if len(sys.argv) > 3:
       if sys.argv[3] == "true" or sys.argv[3] == "false":
           dump_flag = sys.argv[3]
       else:
            algorithm = sys.argv[3]
            
    if len(sys.argv) == 5:
        dump_flag = sys.argv[4]
    
    '''
    Checking if search trace should be dumped or not.
    '''
    dump_flag = dump_flag.lower()
    if dump_flag == "true":
        search_trace = True
    else:
        search_trace = False
    
    '''
    Opening the start and goal file to pass it along to the class object.
    '''
    with open(start_file, 'r') as f:
        lines = [line.strip().split() for line in f.readlines() if not "END" in line]
        puzzle_start = [list(map(int, line)) for line in lines]

    with open(goal_file, 'r') as f:
        lines = [line.strip().split() for line in f.readlines() if not "END" in line]
        puzzle_goal = [list(map(int, line)) for line in lines]
    
    puzzle = Expense_Puzzle(puzzle_start, puzzle_goal)
    
    
    '''
    Based on what algorithm/method was used, the correct function will be called
    with the correct parameters.
    '''
    if algorithm == "bfs":
        trace_filename, steps, cost = puzzle.bfs(search_trace)
    
    elif algorithm == "ucs":
        trace_filename, steps, cost = puzzle.ucs(search_trace)
   
    elif algorithm == "dfs":
        trace_buffer, steps, cost = puzzle.dfs(search_trace)
        if search_trace:
            time = datetime.datetime.now()
            file_time = time.strftime('%Y%m%d-%H%M%S')
            trace_filename = f"trace-{file_time}.txt"
            with open(trace_filename, "a") as f:
                for line in trace_buffer:
                    f.write(line)
    
    elif algorithm == "dls":
        user_input = input("Please enter the Depth Limit: ")
        while not user_input.isdigit():
            print("\nInput has to be a Number.. Try again\n\n")
            user_input = input("Please enter the Depth Limit: ")
        limit = int(user_input)
        trace_buffer, steps, cost = puzzle.dls(limit,search_trace)
        if search_trace:
            time = datetime.datetime.now()
            file_time = time.strftime('%Y%m%d-%H%M%S')
            trace_filename = f"trace-{file_time}.txt"
            with open(trace_filename, "a") as trace_file:
                for line in trace_buffer:
                    trace_file.write(line)
    
    elif algorithm == "ids":
        trace_buffer, steps, cost = puzzle.ids(search_trace)
        if search_trace:
            time = datetime.datetime.now()
            file_time = time.strftime('%Y%m%d-%H%M%S')
            trace_filename = f"trace-{file_time}.txt"
            with open(trace_filename, "a") as trace_file:
                for line in trace_buffer:
                    trace_file.write(line)
        
    elif algorithm == "greedy":
        trace_filename, steps, cost = puzzle.greedy(search_trace)
    else:
        trace_filename, steps, cost = puzzle.a_star(search_trace)
    
    '''
    Based on if solution is found the output will be printed.
    '''
    if steps == None and cost == None:
        print("Solution Not Found")     
    else:
        print(f"Nodes Popped: {puzzle.nodes_popped}")
        print(f"Nodes Expanded: {puzzle.nodes_expanded}")
        print(f"Nodes Generated: {puzzle.nodes_generated}")
        print(f"Max Fringe Size: {puzzle.max_fringe_size}")
        print(f"Solution Found at depth {len(steps)} with cost of {cost}.")
        print("Steps:")
        for step in steps:
            print(f"\t{step}")

    '''
    Adding the final output to the search trace dump file
    '''
    if search_trace:
        with open(trace_filename, "a") as trace_file:
            if steps == None and cost == None:
                trace_file.write("Solution Not Found")     
            else:
                trace_file.write("\n\n\nFinal Output\n\n")
                trace_file.write(f"Nodes Popped: {puzzle.nodes_popped}\n")
                trace_file.write(f"Nodes Expanded: {puzzle.nodes_expanded}\n")
                trace_file.write(f"Nodes Generated: {puzzle.nodes_generated}\n")
                trace_file.write(f"Max Fringe Size: {puzzle.max_fringe_size}\n")
                trace_file.write(f"Solution Found at depth {len(steps)} with cost of {cost}.\n")
                