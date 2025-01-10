# Intro to Artificial Intelligence Week 1 Notes

## Agents

### Situated Agent
![alt text](diagrams/situated_agent.png)
**Agents**
- an entity that performs action in its environment
- agent + environment = world
- inside the **black box** is the **belief state**

**example of application domains**
- Autonomous delivery robot
    - roam around an office environment and delivers coffee, parcels.
-  Diagnostic assistant
    - help human troubleshoot problems and suggest repairs.

**Domain for delivery robot**

The robot must:
- Deliver coffee & mail when needed
- avoid getting wet

**Delivery robot**
- Abilities: movement, speech, pickup and place items, sense weather
- Stimuli: environmental information from camera, sonar, sound, laser range finder, keyboards.
- Prior knowledge: know its capabilityies, objects it may encounter, maps
- Past experiences: which actions are useful and when, what objects are there and how its actions affect its position.
- Goals: what it needs to deliver and when, tradeoff between acting quickly and acting safely, effect of getting wet.

**What the robot needs to do**  
- Determine user location
- Path finding between locations
- Planning to carry out multiple task
- make default assumptions about where user is.
- make tradeoffs under uncertainty.
- learn from experience.
- sense and act in the world

**Knowledge representation**
- knowledge: information used to solve tasks
- representation : data structures used to encode knowledge
- knowledge base (KB): representation of all knowledge.
- model: relationship of kb to world
- level of abstraction: accuracy of model
- Non-AI:
    - Specify how to compute something
    - Specify what the next step is
    - programmer does the computation
- AI:
    - Specify what needs to be computed
    - Specify how the world works
    - Agent figures out how to do the computation

### Dimensions of Complexity: 
1. **Modularity**: flat --> modular --> hierarchical
2. **Planning horizon**: non-planning --> finite horizon --> indefinite horizon --> infinite horizon
3. **Representation**: explicit states --> features --> individuals and relations
4. **Computational limits**: perfect rationality --> bounded rationality
5. **Learning**: knowledge is given --> knowledge is learned
6. **Uncertainty**: fully observable --> partially observable
7. **Preference**: goals --> complex preferences.
8. **Reasoning by number of agents**: single agent --> adversarial --> multiagent
9. **Interactivity**: offlie --> online

**Planning horizon**  
How far the agent looks into the future when deciding what to do.
- Static: world doesn't change
- Finite horizon: agent reasons about a fixed finite number of time steps
- Indefinite horizon: agent is reasoning about finite, but not predetermined, number of time steps (e.g until goal completiong)
- Infinite horizon: agent plans for going on forever (process oriented)

**Representation**
Finding compact representations and exploiting that compactness for computational gains.
- Explicit states: state directly represents one way the world could be
- Features or propositions: 
    - more natural ot describe states in terms of features
    - 30 binary features can represent 2<sup>30</sup> states.
- Individuals and relations
    - There is a feature for each relationship on each tuple of individuals
    - we can reason without knowing the individuals or when there are infinitely many individuals.
    ![alt text](diagrams/relations.png)

**Computational limits**
Feasible to calculate the exact solutions?
- Perfect rationality: agent always choose the optimal action
- Bounded rationality: agent chooses a possibly sub-optimal action given its limited computational capacity (e.g chess bot)
    - Satisficing (good enough) solution
    - Approximately optimal solution


**Learing from experience**  
Is the model's knowledge given or learned from experience.

**Uncertainty**  
- Fully-observable: the agent knows the state of the world from observations
- Partially-observable: there can be many stats that are possible given an observation

**Uncertain world dynamics**  
If the agent knew the initial state and the action, can it predict the resulting state?
- Deterministic: state resulting from carrying out an action in state is determined from the action and the state.
- Stochastic: there is uncertainty over the states resulting from executing a given action in a given state.

**Goals or Complex preferences**  
- Achievement goal: goal to achieve (e.g complex logical formula)
- Maintenance goal: is goal to be maintained
- Complex preferences: involve tradeoffs between various desiderata, perhaps at different times, can be ordinal or cardinal.
    - e.g coffee delivery robot, medical doctor.
    - Goals may conflict
    - Goals may be combinatorial
    - Goals may change

**Reasoning by number of agents**  
- Single agent: agent assumes other agents are part of environment
- Adversarial: considers another agent that acts in opposiotion to our goal
- Multiagent: agent needs to reason strategically about reasoning of other agents (e.g trading agents)

Agents can have their own goals: cooperative, competitive, independant goals.

## Uninformed Search

**Searching**  
Search for the solution by exploring a **directed graph** that represents the **state space**

**Directed graphs**
- N nodes
- A edges/arcs (pais of nodes)
- Path, i.e a sequence of nodes such that (n<sub>1</sub>,n<sub>2</sub>) ⊆ A.
- Cost associated with arcs.

**Search problem**
- set of states
- initial state
- goal states or goal test
    - boolean function which tells whether a given state is a goal state
- Successor (neighbour) function
    - action which takes us from one state to other state
- Cost associated with each action (optional)

**Graph Search Algorithm**
```
Input: A graph, a set of start nodes, Boolean procedure goal(n)
that tests if n is a goal node
1: frontier ←{⟨s⟩: s is a start node}
2: while frontier is not empty do
3: select and remove path ⟨n0, . . . , nk⟩from frontier
4: if goal(nk) then
5: return ⟨n0, . . . , nk⟩
6: for each neighbor n of nk do
7: add ⟨n0, . . . , nk, n⟩to frontier
```

**Depth-First search**
- Uses a stack
