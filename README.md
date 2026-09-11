*This project has been created as part of the 42 curriculum by ascheufe.*

# <center>Fly-In</center>
> [!NOTE]
> This project was fully done without AI usage. Meaning no AI has been used for help in the coding process, research or anything else.

# Description
The goal is to create a python program that can take any given map in the correct schema parse it and run a simulation of drones over it. It will then give you a log file and a visual representation showing how the drones would navigate the given map.
To achieve solve the node graph (zone and connections) a pathfinding algorithm was needed, I chose dijkstra as its a good fit for node graphs that do not yet have any kind of huristic.  

## Parsing:
Correct example map:
```
# Easy Level 1: Simple linear path
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

Wrong example map:
```
# Easy Level 1: Simple linear path
nb_drones: -1 # Number of drones cant be negative or 0

start_hub: start 0 a [color=green]		# Coordinate must be valid integer not 'a'.
hub: waypoint1 1 0 [speed=12]			# Key speed does not exist as metadata.
hub: waypoint2							# No coordinates provided.
end_hub: goal 3 0 [color=red] blabla	# Unknown extra text.

connection: start-doesNotExist			# Hub not defined in hubs above.
connection: waypoint1-nameWith-Dash		# No dash allowed in hub name.
connection: waypoint2-waypoint2			# Connection connected to itself.
```

## Parser Constraints
*This is copied from the subject pdf*
#### The input file must respect the expected structure and syntax:
• The first line must define the number of drones using nb_drones: <positive_integer>.\
• The program must be able to handle any number of drones.\
• There must be exactly one start_hub: zone and one end_hub: zone.\
• Each zone must have a unique name and valid integer coordinates.\
• Zone names can use any valid characters but dashes and spaces.\
• Connections must link only previously defined zones using connection: <zone1>-<zone2> [metadata].\
• The same connection must not appear more than once (e.g., a-b and b-a are considered duplicates).\
• Any metadata block (e.g., [zone=... color=...] for zones, [max_link_capacity=...] for connections) must be syntactically valid.\
• Zone types must be one of: normal, blocked, restricted, priority. Any invalid type must raise a parsing error.\
• Capacity values (max_drones for zones, max_link_capacity for connections) must be positive integers.\
• Any other parsing error must stop the program and return a clear error message indicating the line and cause.

![](docs/error%20parsing.gif)

## Visual Representation/Path finding
### Visual representation has been done with the `Pygame-ce` package
Simple Example

![](docs/simple%20example.gif)
----------
![](docs/showcase.webm)
