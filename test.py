def detect_collision(robot1, robot2):
    for step1 in robot1["path"]:
        for step2 in robot2["path"]:
            if step1["x"] == step2["x"] and step1["y"] == step2["y"] and step1["z"] == step2["z"]:
                print("Collision detected at ({}, {}, {})".format(step1["x"], step1["y"], step1["z"]))
                return True
    print("No collision detected")
    return False

def reroute_robot(robot, other_robot):
    # Find the last common position between the two robots' paths
    common_position = None
    for step in reversed(robot["path"]):
        if step in other_robot["path"]:
            common_position = step
            break

    if common_position:
        # Find the index of the common position in the robot's path
        common_index = robot["path"].index(common_position)

        # Reroute the robot by incrementing or decrementing x or y coordinate
        for i in range(common_index + 1, len(robot["path"])):
            # Example: Increment x coordinate
            robot["path"][i]["x"] += 1

        # Update the original robots list with the modified path
        index = robots.index(robot)
        robots[index]["path"] = robot["path"]


def adjust_paths(robots):
    for i in range(len(robots)):
        for j in range(i + 1, len(robots)):
            if detect_collision(robots[i], robots[j]):
                # Adjust paths to avoid collision between robots[i] and robots[j]
                reroute_robot(robots[i], robots[j])
                # You may also implement other collision resolution strategies here
                # such as temporary pausing of one of the robots

# Example usage
robot1 = [{"x": 0, "y": 0, "z": 0}, {"x": 1, "y": 1, "z": 0}, {"x": 2, "y": 0, "z": 0}]
robot2 = [{"x": 0, "y": 1, "z": 0}, {"x": 1, "y": 1, "z": 0}, {"x": 2, "y": 1, "z": 0}]
robots = [robot1, robot2]

print("Initial paths:")
for robot in robots:
    print(robot["path"])

adjust_paths(robots)

print("\nPaths after adjustment:")
for robot in robots:
    print(robot["path"])
