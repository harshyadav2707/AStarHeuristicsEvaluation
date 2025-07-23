import math

def manhattan(p1, p2):
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

def euclidean(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def diagonal(p1, p2):
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    return max(dx, dy)

# Hybrid heuristic: weighted combination of Manhattan and Euclidean
def hybrid(p1, p2, w1=0.5, w2=0.5):
    return w1 * manhattan(p1, p2) + w2 * euclidean(p1, p2)
