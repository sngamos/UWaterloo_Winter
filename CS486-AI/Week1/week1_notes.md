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

