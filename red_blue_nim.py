import sys

class Marble_State:
    '''
    We use this class to keep track of the properties of the game state
    '''
    def __init__(self, red, blue, first_player, version):
        self.red = red
        self.blue = blue
        self.first_player = first_player
        self.version = version

def utility(state_obj):
    '''
    We use this to calculate the score and return either a positive or negative
    value depending on whether it is a standard or misere game
    '''
    utility_value = 2 * state_obj.red + 3 * state_obj.blue
    return utility_value if state_obj.version == "standard" else -abs(utility_value)

def successors(state_obj):
    '''
    We will calculate all possible successors for the computer to choose a move from
    and return the list.
    '''
    successors_list = []
    moves = [(state_obj.blue, state_obj.red - 1, state_obj.blue), 
                  (state_obj.red, state_obj.red, state_obj.blue - 1)]
    
    if state_obj.version == "misère": moves.reverse()
    
    for move_value, new_red, new_blue in moves:
        if move_value > 0:
            successors_list.append(Marble_State(new_red, new_blue, state_obj.first_player, state_obj.version))

    return successors_list

def max_value(state_obj, alpha, beta):
    '''
    Citation: 
        - https://crystal.uta.edu/~gopikrishnav/classes/common/4308_5360/slides/alpha_beta.pdf
        - https://crystal.uta.edu/~gopikrishnav/classes/common/4308_5360/slides/Game_Search.pdf
    Code for this function was created using the pseduocode given in the class slides 
    mentioned above, therefore the code will be similar to the one in the slides.
    
    We check for a terminal state and return the utlity if that is true,
    then we use the possible successors for the game state and return the 
    largest value.
    '''
    if state_obj.red == 0 or state_obj.blue == 0:
        return utility(state_obj)
    value = -float('inf')
    successors_list = successors(state_obj)
    for successor in successors_list:
        value = max(value, min_value(successor, alpha, beta))
        if value >= beta:
            return value
        alpha = max(alpha, value)
    return value

def min_value(state_obj, alpha, beta):
    '''
    Citation: 
        - https://crystal.uta.edu/~gopikrishnav/classes/common/4308_5360/slides/alpha_beta.pdf
        - https://crystal.uta.edu/~gopikrishnav/classes/common/4308_5360/slides/Game_Search.pdf
    Code for this function was created using the pseduocode given in the class slides 
    mentioned above, therefore the code will be similar to the one in the slides.
    
    We check for a terminal state and return the utlity if that is true,
    then we use the possible successors for the game state and return the 
    smallest value.
    '''
    if state_obj.red == 0 or state_obj.blue == 0:
        return utility(state_obj) 
    value = float('inf')
    successors_list = successors(state_obj)
    for successor in successors_list:
        value = min(value, max_value(successor, alpha, beta))
        if value <= alpha:
            return value
        beta = min(beta, value)
    return value

def alpha_beta_decision(state_obj):
    '''
    Citation: 
        - https://crystal.uta.edu/~gopikrishnav/classes/common/4308_5360/slides/alpha_beta.pdf
        - https://crystal.uta.edu/~gopikrishnav/classes/common/4308_5360/slides/Game_Search.pdf
    Code for this function was created using the pseduocode given in the class slides 
    mentioned above, therefore the code will be similar to the one in the slides.
    
    We will take the successor values that are returned and return the 
    maximum one which will be our decision.
    '''
    successor_values = [(s, min_value(s, -float('inf'), float('inf'))) for s in successors(state_obj)]
    decision = max(successor_values, key=lambda x: x[1], default=(None, -float('inf')))
            
    return decision[0]

def main():
    '''
    We will be doing the setup of the program here to get user input from the 
    command line and instantiate the neccesary variables to start the game.
    '''
    num_red, num_blue = sys.argv[1],sys.argv[2]
    version = "standard"
    first_player = "computer"
    if len(sys.argv) > 3:
       if sys.argv[3] == "standard" or sys.argv[3] == "misere":
           version = sys.argv[3].lower()
       else:
           first_player = sys.argv[3].lower()
            
    if len(sys.argv) == 5:
        first_player = sys.argv[4].lower()
    
    state_obj = Marble_State(int(num_red), int(num_blue), first_player, version)
    current_player  = first_player
    
    '''
    We will begin the game here by using a while loop to alternate between
    the computer and the human and perform the moves that each one chooses
    '''
    print("Let's start the Game!\nHere is the Initial State:")
    print(f"Red Marble Count = {state_obj.red}, Blue Marble Count = {state_obj.blue}")
    while not(state_obj.red == 0 or state_obj.blue == 0):
        if current_player == 'human':
            print(f"\nCurrent Game State: Red Marble Count = {state_obj.red}, Blue Marble Count = {state_obj.blue}")
            move = input("What color marble do you pick?(red/blue)? ").strip().lower()
            while move != 'red' and move != 'blue':
                move = input("Please choose 'red' or 'blue' ONLY: ").strip().lower()
    
            if move == "red":
                state_obj.red -= 1
            else:
                state_obj.blue -= 1
           
        else: 
            state_obj = alpha_beta_decision(state_obj)
    
        current_player = 'computer' if current_player == 'human' else 'human'
    
    '''
    We will calculate the score and output here and display it on the screen
    where we decide who had the last state of the game and decide the winner 
    and loser based on that.
    '''
    score = abs(utility(state_obj))
    other_player = ""
    other_player = 'computer' if current_player == 'human' else 'human'
    if version == "standard":     
        print(f"\n{other_player} won by a score of {score}\n{current_player} lost by a score of {score}")
    else:
        print(f"\n{current_player} won by a score of {score}\n{other_player} lost by a score of {score}")

    print("Game over!")
    
if __name__ == "__main__":

    main()