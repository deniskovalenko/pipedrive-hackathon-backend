from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
#import numpy as np

# Distance callback
class CreateDistanceCallback(object):
  """Create callback to calculate distances between points."""
  def __init__(self, matrix):
    """Array of distances between points."""

    self.matrix = matrix

  def Distance(self, from_node, to_node):
    return int(self.matrix[from_node][to_node])

def tsp(IDs, matrix):
    # locations
    locations = IDs
    tsp_size = len(locations)
    num_routes = 1  # The number of routes, which is 1 in the TSP.
    # Nodes are indexed from 0 to tsp_size - 1. The depot is the starting node of the route.
    depot = 0

    # Create routing model
    if tsp_size > 0:
        routing = pywrapcp.RoutingModel(tsp_size, num_routes, depot)
        search_parameters = pywrapcp.RoutingModel.DefaultSearchParameters()

        # Create the distance callback, which takes two arguments (the from and to node indices)
        # and returns the distance between these nodes.
        my_matrix = matrix

        dist_between_nodes = CreateDistanceCallback(my_matrix)
        dist_callback = dist_between_nodes.Distance
        routing.SetArcCostEvaluatorOfAllVehicles(dist_callback)
        # Solve, returns a solution if any.
        assignment = routing.SolveWithParameters(search_parameters)
        if assignment:
            # Solution cost.
            #print("Total distance: " + str(assignment.ObjectiveValue()) + " miles\n")
            # Inspect solution.
            # Only one route here; otherwise iterate from 0 to routing.vehicles() - 1
            route_number = 0
            index = routing.Start(route_number)  # Index of the variable for the starting node.
            route = []

            while not routing.IsEnd(index):
                # Convert variable indices to node indices in the displayed route.

                route.append(locations[routing.IndexToNode(index)])
                index = assignment.Value(routing.NextVar(index))

            route.append(locations[routing.IndexToNode(index)])
            #print(route)
            return([route,assignment.ObjectiveValue()])
        else:
            print('No solution found.')
    else:
        print('Specify an instance greater than 0.')


if __name__ == '__main__':
  a = tsp(['first', 'second', '3d', '4th'], [[0,18,12,13],
                                             [10,0,11,12],
                                             [10,11,0,13],
                                             [10,11,12,0]])
  print(a)
