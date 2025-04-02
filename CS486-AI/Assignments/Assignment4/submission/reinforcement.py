import random
import numpy as np
import matplotlib.pyplot as plt
import math
class Sender:
    """
    A Q-learning agent that sends messages to a Receiver

    """

    def __init__(self, num_sym:int, grid_rows:int, grid_cols:int, alpha_i:float, alpha_f:float, num_ep:int, epsilon:float, discount:float):
        """
        Initializes this agent with a state, set of possible actions, and a means of storing Q-values

        :param num_sym: The number of arbitrary symbols available for sending
        :type num_sym: int
        :param grid_rows: The number of rows in the grid
        :type grid_rows: int
        :param grid_cols: The number of columns in the grid
        :type grid_cols: int
        :param alpha_i: The initial learning rate
        :type alpha: float
        :param alpha_f: The final learning rate
        :type alpha: float
        :param num_ep: The total number of episodes
        :type num_ep: int
        :param epsilon: The epsilon in epsilon-greedy exploration
        :type epsilon: float
        :param discount: The discount factor
        :type discount: float
        """
        self.actions = range(num_sym)
        self.alpha = alpha_i
        self.alpha_i = alpha_i
        self.alpha_f = alpha_f
        self.num_ep = num_ep
        self.epsilon = epsilon
        self.discount = discount
        self.q_vals = np.zeros((grid_rows,grid_cols, num_sym))

    def select_action(self, state):
        """
        This function is called every time the agent must act. It produces the action that the agent will take
        based on its current state

        :param state: the state the agent is acting from, in the form (x,y), which are the coordinates of the prize
        :type state: (int, int)
        :return: The symbol to be transmitted (must be an int < N)
        :rtype: int
        """
        x,y = state
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            return int(np.argmax(self.q_vals[y,x,:]))

    def update_q(self, old_state, action, reward):
        """
        This function is called after an action is resolved so that the agent can update its Q-values

        :param old_state: the state the agent was in when it acted, in the form (x,y), which are the coordinates
                          of the prize
        :type old_state: (int, int)
        :param action: the action that was taken
        :type action: int
        :param reward: the reward that was received
        :type reward: float
        """
        x, y = old_state
        current = self.q_vals[y,x,action]
        self.q_vals[y,x,action] = (1-self.alpha) * current + self.alpha * reward



class Receiver:
    """
    A Q-learning agent that receives a message from a Sender and then navigates a grid

    """

    def __init__(self, num_sym:int, grid_rows:int, grid_cols:int, alpha_i:float, alpha_f:float, num_ep:int, epsilon:float, discount:float):
        """
        Initializes this agent with a state, set of possible actions, and a means of storing Q-values

        :param num_sym: The number of arbitrary symbols available for sending
        :type num_sym: int
        :param grid_rows: The number of rows in the grid
        :type grid_rows: int
        :param grid_cols: The number of columns in the grid
        :type grid_cols: int
        :param alpha_i: The initial learning rate
        :type alpha: float
        :param alpha_f: The final learning rate
        :type alpha: float
        :param num_ep: The total number of episodes
        :type num_ep: int
        :param epsilon: The epsilon in epsilon-greedy exploration
        :type epsilon: float
        :param discount: The discount factor
        :type discount: float
        """
        self.actions = [0,1,2,3] # Note: these correspond to [up, down, left, right]
        self.alpha = alpha_i
        self.alpha_i = alpha_i
        self.alpha_f = alpha_f
        self.num_ep = num_ep
        self.epsilon = epsilon
        self.discount = discount
        self.q_vals = np.zeros((num_sym,grid_rows,grid_cols, len(self.actions)))

    def select_action(self, state):
        """
        This function is called every time the agent must act. It produces the action that the agent will take
        based on its current state
        :param state: the state the agent is acting from, in the form (m,x,y), where m is the message received
                      and (x,y) are the board coordinates
        :type state: (int, int, int)
        :return: The direction to move, where 0 is up, 1 is down, 2 is left, and 3 is right
        :rtype: int
        """
        m,x,y = state
        if random.random() < self.epsilon:
            return random.choice(self.actions)
        else:
            return int(np.argmax(self.q_vals[m,y,x,:]))

    def update_q(self, old_state, new_state, action, reward):
        """
        This function is called after an action is resolved so that the agent can update its Q-values

        :param old_state: the state the agent was in when it acted in the form (m,x,y), where m is the message received
                          and (x,y) are the board coordinates
        :type old_state: (int, int, int)
        :param new_state: the state the agent entered after it acted
        :type new_state: (int, int, int)
        :param action: the action that was taken
        :type action: int
        :param reward: the reward that was received
        :type reward: float
        """
        m_old , x_old, y_old = old_state
        m_new , x_new, y_new = new_state
        current = self.q_vals[m_old,y_old,x_old,action]
        future = np.max(self.q_vals[m_new,y_new,x_new,:])
        self.q_vals[m_old,y_old,x_old,action] = (1-self.alpha) * current + self.alpha * (reward + self.discount * future)


def get_grid(grid_name:str):
    """
    This function produces one of the three grids defined in the assignment as a nested list

    :param grid_name: the name of the grid. Should be one of 'fourroom', 'maze', or 'empty'
    :type grid_name: str
    :return: The corresponding grid, where True indicates a wall and False a space
    :rtype: list[list[bool]]
    """
    grid = [[False for i in range(5)] for j in range(5)] # default case is 'empty'
    if grid_name == 'fourroom':
        grid[0][2] = True
        grid[2][0] = True
        grid[2][1] = True
        grid[2][3] = True
        grid[2][4] = True
        grid[4][2] = True
    elif grid_name == 'maze':
        grid[1][1] = True
        grid[1][2] = True
        grid[1][3] = True
        grid[2][3] = True
        grid[3][1] = True
        grid[4][1] = True
        grid[4][2] = True
        grid[4][3] = True
        grid[4][4] = True
    return grid


def legal_move(posn_x:int, posn_y:int, move_id:int, grid:list[list[bool]]):
    """
    Produces the new position after a move starting from (posn_x,posn_y) if it is legal on the given grid (i.e. not
    out of bounds or into a wall)

    :param posn_x: The x position (column) from which the move originates
    :type posn_x: int
    :param posn_y: The y position (row) from which the move originates
    :type posn_y: int
    :param move_id: The direction to move, where 0 is up, 1 is down, 2 is left, and 3 is right
    :type move_id: int
    :param grid: The grid on which to move, where False indicates a space and True a wall
    :type grid: list[list[bool]]
    :return: The new (x,y) position if the move was legal, or the old position if it was not
    :rtype: (int, int)
    """
    moves = [[0,-1],[0,1],[-1,0],[1,0]]
    new_x = posn_x + moves[move_id][0]
    new_y = posn_y + moves[move_id][1]
    result = (new_x,new_y)
    if new_x < 0 or new_y < 0 or new_x >= len(grid[0]) or new_y >= len(grid):
        result = (posn_x,posn_y)
    else:
        if grid[new_y][new_x]:
            result = (posn_x,posn_y)
    return result


def run_episodes(sender:Sender, receiver:Receiver, grid:list[list[bool]], num_ep:int, delta:float):
    """
    Runs the reinforcement learning scenario for the specified number of episodes

    :param sender: The Sender agent
    :type sender: Sender
    :param receiver: The Receiver agent
    :type receiver: Receiver
    :param grid: The grid on which to move, where False indicates a space and True a wall
    :type grid: list[list[bool]]
    :param num_ep: The number of episodes
    :type num_ep: int
    :param delta: The chance of termination after every step of the receiver
    :type delta: float [0,1]
    :return: A list of the reward received by each agent at the end of every episode
    :rtype: list[float]
    """
    reward_vals = []

    # Episode loop
    for ep in range(num_ep):
        # Set receiver starting position
        receiver_x = 2
        receiver_y = 2

        # Choose prize position
        prize_x = np.random.randint(len(grid[0]))
        prize_y = np.random.randint(len(grid))
        while grid[prize_y][prize_x] or (prize_x == receiver_x and prize_y == receiver_y):
            prize_x = np.random.randint(len(grid[0]))
            prize_y = np.random.randint(len(grid))

        # Initialize new episode
        # Sender selects a message based on the prize position state (x, y)
        message = sender.select_action((prize_x, prize_y))

        # Receiver loop
        # (receiver acts, check for prize, check for random termination, update receiver Q-value)
        # Initialize the receiver state as (message, x, y)
        state = (message, receiver_x, receiver_y)
        episode_reward = 0
        terminate = False
        while not terminate:
            old_state = state
            # Receiver selects a move
            action = receiver.select_action(old_state)
            # Compute new position using legal_move
            new_x, new_y = legal_move(old_state[1], old_state[2], action, grid)
            new_state = (message, new_x, new_y)
            
            # Check if the receiver has found the prize
            if new_x == prize_x and new_y == prize_y:
                reward = 1.0
                episode_reward = 1.0
                receiver.update_q(old_state, new_state, action, reward)
                terminate = True
            # Otherwise, check for random termination (with probability delta)
            elif random.random() < delta:
                reward = 0.0
                receiver.update_q(old_state, new_state, action, reward)
                terminate = True
            else:
                reward = 0.0
                receiver.update_q(old_state, new_state, action, reward)
                state = new_state  # continue from new state

        #Finish up episode
        # (update sender Q-value, update alpha values, append reward to output list)
        sender.update_q((prize_x, prize_y), message, episode_reward)
        
        # Linearly decay the learning rate for both agents
        new_alpha = sender.alpha_i - (sender.alpha_i - sender.alpha_f) * (ep / num_ep)
        sender.alpha = new_alpha
        receiver.alpha = new_alpha

        reward_vals.append(episode_reward)

    return reward_vals

### main function for qn 2 part 1
'''
if __name__ == "__main__":
    # Parameters
    num_learn_episodes = 100000
    num_test_episodes = 1000
    grid_name = 'fourroom'  # Options: 'fourroom', 'maze', 'empty'
    grid = get_grid(grid_name)
    num_signals = 4
    discount = 0.95
    delta = 1 - discount  # termination probability per receiver step
    epsilon = 0.1
    alpha_init = 0.9
    alpha_final = 0.01

    # Initialize agents (grid rows and grid cols are len(grid) and len(grid[0]) respectively)
    sender = Sender(num_signals, len(grid), len(grid[0]), alpha_init, alpha_final, num_learn_episodes, epsilon, discount)
    receiver = Receiver(num_signals, len(grid), len(grid[0]), alpha_init, alpha_final, num_learn_episodes, epsilon, discount)

    # Learning phase
    learn_rewards = run_episodes(sender, receiver, grid, num_learn_episodes, delta)

    # Switch to testing: disable exploration and learning updates.
    sender.epsilon = 0.0
    sender.alpha = 0.0
    sender.alpha_i = 0.0
    sender.alpha_f = 0.0
    receiver.epsilon = 0.0
    receiver.alpha = 0.0
    receiver.alpha_i = 0.0
    receiver.alpha_f = 0.0
    test_rewards = run_episodes(sender, receiver, grid, num_test_episodes, delta)

    # Print average rewards during learning and testing
    print("Average reward during learning: " + str(np.average(learn_rewards)))
    print("Average reward during testing: " + str(np.average(test_rewards)))
'''
### main function for qn 2 part 2
'''
if __name__ == "__main__":

    # Grids and discount factor
    grid_name = 'fourroom'   # 'fourroom', 'maze', or 'empty'
    grid = get_grid(grid_name)
    discount = 0.95
    delta = 1 - discount

    # You will vary these:
    Nep_list = [10, 100, 1000, 10000, 50000, 100000]
    epsilons = [0.01, 0.1, 0.4]
    num_signals = 4

    # Other fixed parameters
    alpha_init = 0.9
    alpha_final = 0.01
    num_test_episodes = 1000
    num_runs = 10   # number of trials for each setting

    # Data structure to store average test rewards:
    # test_results[epsilon][Nep] = list of length num_runs (the test rewards)
    test_results = {eps: {nep: [] for nep in Nep_list} for eps in epsilons}

    for eps in epsilons:
        for nep in Nep_list:
            for run_i in range(num_runs):
                # 1) Initialize agents
                sender = Sender(num_signals,
                                len(grid),
                                len(grid[0]),
                                alpha_init,
                                alpha_final,
                                nep,           # <--- the number of learning episodes
                                eps,           # <--- the epsilon
                                discount)

                receiver = Receiver(num_signals,
                                    len(grid),
                                    len(grid[0]),
                                    alpha_init,
                                    alpha_final,
                                    nep,
                                    eps,
                                    discount)

                # 2) Learn (train)
                learn_rewards = run_episodes(sender, receiver, grid, nep, delta)

                # 3) Test (with eps=0, alpha=0)
                sender.epsilon = 0.0
                sender.alpha = 0.0
                receiver.epsilon = 0.0
                receiver.alpha = 0.0
                test_rewards = run_episodes(sender, receiver, grid, num_test_episodes, delta)

                # Record the average test reward for this run
                test_results[eps][nep].append(np.mean(test_rewards))

    # Now plot results: For each eps, plot average discounted reward vs. log(Nep)
    fig, ax = plt.subplots()
    for eps in epsilons:
        means = []
        stds = []
        for nep in Nep_list:
            vals = test_results[eps][nep]
            means.append(np.mean(vals))
            stds.append(np.std(vals))

        # On x-axis, we can use log10(Nep)
        xvals = [math.log10(n) for n in Nep_list]
        ax.errorbar(xvals, means, yerr=stds, label=f'eps={eps}', capsize=3)

    ax.set_xlabel('log10(Nep)')
    ax.set_ylabel('Average Discounted Reward (Test)')
    ax.set_title('Learning Curves on Four-Room Grid')
    ax.legend()
    plt.show()
    # Suppose we have already done the learning
    # Now we extract the policies:

    def arrow_for_action(a):
        return {0:'^', 1:'v', 2:'<', 3:'>'}[a]

    print("Sender's Policy (which message is chosen for each possible prize location):")
    for y in range(len(grid)):
        row_symbols = []
        for x in range(len(grid[0])):
            if grid[y][x]:
                row_symbols.append('X')  # wall
            else:
                best_msg = np.argmax(sender.q_vals[y, x, :])
                row_symbols.append(str(best_msg))
        print(" ".join(row_symbols))

    print("\nReceiver's Policy (arrows) for each message:")
    for m in range(4):
        print(f"\nMessage {m}:")
        for y in range(len(grid)):
            row_arrows = []
            for x in range(len(grid[0])):
                if grid[y][x]:
                    row_arrows.append('X')  # wall
                else:
                    best_dir = np.argmax(receiver.q_vals[m, y, x, :])
                    row_arrows.append(arrow_for_action(best_dir))
            print(" ".join(row_arrows))
'''

## main function for qn 2 part 3
'''
if __name__ == "__main__":
    # Get the grid (using the 'fourroom' grid as provided)
    grid_name = 'fourroom'
    grid = get_grid(grid_name)
    discount = 0.95
    delta = 1 - discount  # termination probability per receiver step

    # Define the training episodes and fixed epsilon
    Nep_list = [10, 100, 1000, 10000, 50000, 100000]
    epsilon = 0.1  # fixed epsilon value for these tests
    num_signals_list = [2, 4, 10]  # N values to test

    # Other parameters
    alpha_init = 0.9
    alpha_final = 0.01
    num_test_episodes = 1000  # testing phase episodes
    num_runs = 10  # number of tests per combination

    # Dictionary to store test results:
    # test_results[num_signals][Nep] = list of average test rewards (one per run)
    test_results = {ns: {nep: [] for nep in Nep_list} for ns in num_signals_list}

    for ns in num_signals_list:
        for nep in Nep_list:
            for run in range(num_runs):
                # Initialize the sender and receiver agents with current num_signals and Nep
                sender = Sender(ns, len(grid), len(grid[0]), alpha_init, alpha_final, nep, epsilon, discount)
                receiver = Receiver(ns, len(grid), len(grid[0]), alpha_init, alpha_final, nep, epsilon, discount)

                # Training phase: run for 'nep' episodes
                learn_rewards = run_episodes(sender, receiver, grid, nep, delta)

                # Testing phase: disable exploration and learning by setting epsilon and alpha to 0.
                sender.epsilon = 0.0
                sender.alpha = 0.0
                receiver.epsilon = 0.0
                receiver.alpha = 0.0
                test_rewards = run_episodes(sender, receiver, grid, num_test_episodes, delta)

                # Compute average test reward for this run
                avg_test_reward = np.mean(test_rewards)
                test_results[ns][nep].append(avg_test_reward)

    # Plot the results: one line per num_signals (N) value
    fig, ax = plt.subplots()
    for ns in num_signals_list:
        means = []
        stds = []
        for nep in Nep_list:
            rewards = test_results[ns][nep]
            means.append(np.mean(rewards))
            stds.append(np.std(rewards))
        # Use log10(Nep) for the x-axis
        xvals = [math.log10(n) for n in Nep_list]
        ax.errorbar(xvals, means, yerr=stds, capsize=3, label=f'N = {ns}')

    ax.set_xlabel('log10(Nep)')
    ax.set_ylabel('Average Discounted Reward (Test)')
    ax.set_title('Test Performance on Four-Room Grid (ε = 0.1)')
    ax.legend()
    plt.show()
'''
## main function for qn 2 part 4
'''
if __name__ == "__main__":
    # Get the grid (using the 'maze' grid as provided)
    grid_name = 'maze'
    grid = get_grid(grid_name)
    discount = 0.95
    delta = 1 - discount  # termination probability per receiver step

    # Define the training episodes and fixed epsilon
    Nep_list = [10, 100, 1000, 10000, 50000, 100000]
    epsilon = 0.1  # fixed epsilon value for these tests
    num_signals_list = [2, 3, 5]  # N values to test

    # Other parameters
    alpha_init = 0.9
    alpha_final = 0.01
    num_test_episodes = 1000  # testing phase episodes
    num_runs = 10  # number of tests per combination

    # Dictionary to store test results:
    # test_results[num_signals][Nep] = list of average test rewards (one per run)
    test_results = {ns: {nep: [] for nep in Nep_list} for ns in num_signals_list}

    for ns in num_signals_list:
        for nep in Nep_list:
            for run in range(num_runs):
                # Initialize the sender and receiver agents with current num_signals and Nep
                sender = Sender(ns, len(grid), len(grid[0]), alpha_init, alpha_final, nep, epsilon, discount)
                receiver = Receiver(ns, len(grid), len(grid[0]), alpha_init, alpha_final, nep, epsilon, discount)

                # Training phase: run for 'nep' episodes
                learn_rewards = run_episodes(sender, receiver, grid, nep, delta)

                # Testing phase: disable exploration and learning by setting epsilon and alpha to 0.
                sender.epsilon = 0.0
                sender.alpha = 0.0
                receiver.epsilon = 0.0
                receiver.alpha = 0.0
                test_rewards = run_episodes(sender, receiver, grid, num_test_episodes, delta)

                # Compute average test reward for this run
                avg_test_reward = np.mean(test_rewards)
                test_results[ns][nep].append(avg_test_reward)

    # Plot the results: one line per num_signals (N) value
    fig, ax = plt.subplots()
    for ns in num_signals_list:
        means = []
        stds = []
        for nep in Nep_list:
            rewards = test_results[ns][nep]
            means.append(np.mean(rewards))
            stds.append(np.std(rewards))
        # Use log10(Nep) for the x-axis
        xvals = [math.log10(n) for n in Nep_list]
        ax.errorbar(xvals, means, yerr=stds, capsize=3, label=f'N = {ns}')

    ax.set_xlabel('log10(Nep)')
    ax.set_ylabel('Average Discounted Reward (Test)')
    ax.set_title('Test Performance on Four-Room Grid (ε = 0.1)')
    ax.legend()
    plt.show()
'''
## main function for qn 2 part 5
if __name__ == "__main__":
    # Get the grid (using the 'empty' grid as provided)
    grid_name = 'empty'
    grid = get_grid(grid_name)
    discount = 0.95
    delta = 1 - discount  # termination probability per receiver step

    # Define the training episodes and fixed epsilon
    Nep_list = [10, 100, 1000, 10000, 50000, 100000]
    epsilon = 0.1  # fixed epsilon value for these tests
    num_signals_list = [1]  # N values to test

    # Other parameters
    alpha_init = 0.9
    alpha_final = 0.01
    num_test_episodes = 1000  # testing phase episodes
    num_runs = 10  # number of tests per combination

    # Dictionary to store test results:
    # test_results[num_signals][Nep] = list of average test rewards (one per run)
    test_results = {ns: {nep: [] for nep in Nep_list} for ns in num_signals_list}

    for ns in num_signals_list:
        for nep in Nep_list:
            for run in range(num_runs):
                # Initialize the sender and receiver agents with current num_signals and Nep
                sender = Sender(ns, len(grid), len(grid[0]), alpha_init, alpha_final, nep, epsilon, discount)
                receiver = Receiver(ns, len(grid), len(grid[0]), alpha_init, alpha_final, nep, epsilon, discount)

                # Training phase: run for 'nep' episodes
                learn_rewards = run_episodes(sender, receiver, grid, nep, delta)

                # Testing phase: disable exploration and learning by setting epsilon and alpha to 0.
                sender.epsilon = 0.0
                sender.alpha = 0.0
                receiver.epsilon = 0.0
                receiver.alpha = 0.0
                test_rewards = run_episodes(sender, receiver, grid, num_test_episodes, delta)

                # Compute average test reward for this run
                avg_test_reward = np.mean(test_rewards)
                test_results[ns][nep].append(avg_test_reward)

    # Plot the results: one line per num_signals (N) value
    fig, ax = plt.subplots()
    for ns in num_signals_list:
        means = []
        stds = []
        for nep in Nep_list:
            rewards = test_results[ns][nep]
            means.append(np.mean(rewards))
            stds.append(np.std(rewards))
        # Use log10(Nep) for the x-axis
        xvals = [math.log10(n) for n in Nep_list]
        ax.errorbar(xvals, means, yerr=stds, capsize=3, label=f'N = {ns}')

    ax.set_xlabel('log10(Nep)')
    ax.set_ylabel('Average Discounted Reward (Test)')
    ax.set_title('Test Performance on Four-Room Grid (ε = 0.1)')
    ax.legend()
    plt.show()

