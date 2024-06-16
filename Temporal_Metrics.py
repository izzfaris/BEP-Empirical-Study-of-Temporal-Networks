from collections import defaultdict, deque
from pandas import Timestamp
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def temporal_degree(G):
    '''Function to calculate the temporal degree of each node in the graph.
    
       Input: G - the graph.

       Output: A dictionary with the temporal degree of each node.
    
    '''

    # Initialize a dictionary with default value of int (which is 0)
    temporal_degree_dict = defaultdict(int)

    # Iterate over all edges in the graph
    # u and v are nodes, data is the edge attribute dictionary
    for u, v, data in G.edges(data=True):
        # Increment the degree count for node u
        temporal_degree_dict[u] += 1

        # If the graph is not directed, increment the degree count for node v as well
        # In an undirected graph, each edge contributes to the degree of both nodes
        if not G.is_directed():
            temporal_degree_dict[v] += 1

    # Return the dictionary with temporal degree of each node
    return temporal_degree_dict

def find_temporal_shortest_paths(G, source, target, time_attr): #Used for temporal_betweenness calculation (and Reachability Latency)
    '''Function to find all temporal shortest paths between a source and target node in a graph.

       Input: G - the graph, source - the source node, target - the target node, time_attr - the attribute storing the time information. 

       Output: A list of all temporal shortest paths between the source and target node.
    '''

    # Initialize an empty list to store the shortest paths
    shortest_paths = []

    # Initialize the minimum path length to infinity
    min_length = float('inf')

    # Initialize a queue with the source node, its path, and the last time visited
    queue = deque([(source, [source], -float('inf'))])

    # Initialize a set to keep track of visited nodes
    visited = set()

    # While there are nodes in the queue
    while queue:
        # Dequeue a node, its path, and the last time visited
        current, path, last_time = queue.popleft()

        # If the current node is the target
        if current == target:
            # If the length of the path is less than the minimum length
            if len(path) < min_length:
                # Update the shortest paths and the minimum length
                shortest_paths = [path]
                min_length = len(path)
            # If the length of the path is equal to the minimum length
            elif len(path) == min_length:
                # Add the path to the shortest paths
                shortest_paths.append(path)
            continue

        # If the current node has been visited at the same or a later time, skip it
        if (current, last_time) in visited:
            continue
        # Mark the current node as visited at the current time
        visited.add((current, last_time))

        # Get the neighbors of the current node
        neighbors = G.successors(current) if G.is_directed() else G.neighbors(current)

        # For each neighbor of the current node
        for neighbor in neighbors:
            # For each edge between the current node and the neighbor
            for key, edge_data in G[current][neighbor].items():
                # Get the time of the edge
                edge_time = edge_data[time_attr]
                # If the time is a datetime object, convert it to a timestamp
                if isinstance(edge_time, datetime):
                    edge_time = edge_time.timestamp()  # Convert Timestamp to seconds
                # If the time of the edge is later than the last time visited
                if edge_time > last_time:
                    # Enqueue the neighbor, the path to the neighbor, and the time of the edge
                    queue.append((neighbor, path + [neighbor], edge_time))

    # Return the shortest paths
    return shortest_paths

def temporal_betweenness(G, time_attr='time'):
    '''Function to calculate the temporal betweenness centrality of each node in the graph.
    
       Input: G - the graph, time_attr - the attribute storing the time information.

       Output: A dictionary with the temporal betweenness centrality of each node.
    
    '''
    # Get the list of nodes in the graph
    nodes = list(G.nodes())
    # Get the number of nodes in the graph
    N = len(nodes)
    # Initialize the betweenness centrality of each node to 0
    betweenness = {node: 0 for node in nodes}
    
    # Define a helper function to process a pair of nodes
    def process_pair(s, t):
        # If the nodes are the same, return
        if s == t:
            return
        
        # Find all temporal shortest paths between the nodes
        paths = find_temporal_shortest_paths(G, s, t, time_attr)
        # If there are no paths, return
        if not paths:
            return
        
        # Count the number of paths
        sigma_st = len(paths)
        # Initialize a dictionary to count the number of paths passing through each node
        path_count = defaultdict(int)
        
        # For each path
        for path in paths:
            # For each node in the path (excluding the endpoints)
            for i in range(1, len(path) - 1):
                # Increment the count for the node
                path_count[path[i]] += 1
        
        # For each node
        for node in path_count:
            # Add the fraction of paths passing through the node to its betweenness centrality
            betweenness[node] += path_count[node] / sigma_st
    
    # Create a thread pool executor
    with ThreadPoolExecutor() as executor:
        # For each pair of nodes
        for s in nodes:
            for t in nodes:
                # Submit a task to process the pair
                executor.submit(process_pair, s, t)
    
    # Scale the betweenness centrality of each node by the number of pairs of nodes
    scale = 1 / ((N - 1) * (N - 2))
    for node in betweenness:
        betweenness[node] *= scale
    
    # Return the betweenness centrality of each node
    return betweenness

def temporal_closeness(G, time_attr='time'):
    '''Function to calculate the temporal closeness centrality of each node in the graph.
    
       Input: G - the graph, time_attr - the attribute storing the time information.

       Output: A dictionary with the temporal closeness centrality of each node.
    
    '''
    # Initialize an empty dictionary to store the closeness centrality of each node
    closeness = {}

    # Get the list of nodes in the graph
    nodes = list(G.nodes())

    # Get the number of nodes in the graph
    N = len(nodes)
    
    # For each node in the graph
    for s in nodes:
        # Initialize the distance to each node to infinity
        distance = {node: float('inf') for node in nodes}

        # Set the distance to the current node to 0
        distance[s] = 0

        # Initialize a queue with the current node and the current time
        Q = deque([(s, 0)])  # (node, current_time)
        
        # While there are nodes in the queue
        while Q:
            # Dequeue a node and the current time
            current_node, current_time = Q.popleft()

            # Get the neighbors of the current node
            neighbors = G.successors(current_node) if G.is_directed() else G.neighbors(current_node)
            
            # For each neighbor of the current node
            for neighbor in neighbors:
                # For each edge between the current node and the neighbor
                for key in G[current_node][neighbor]:
                    # Get the time of the edge
                    edge_time = G[current_node][neighbor][key][time_attr]

                    # If the time is a datetime object, convert it to a timestamp
                    if isinstance(edge_time, datetime):
                        edge_time = edge_time.timestamp()  # Convert Timestamp to seconds

                    # If the time of the edge is later than the current time and earlier than the distance to the neighbor
                    if current_time <= edge_time < distance[neighbor]: 
                        # Update the distance to the neighbor
                        distance[neighbor] = edge_time

                        # Enqueue the neighbor and the time of the edge
                        Q.append((neighbor, edge_time))
        
        # Calculate the total reciprocal distance to all reachable nodes
        total_reciprocal_distance = sum([1/d for d in distance.values() if d != float('inf') and d != 0])

        # Count the number of reachable nodes
        reachable_nodes = len([d for d in distance.values() if d != float('inf') and d != 0])
        
        # If there are reachable nodes
        if reachable_nodes > 0:
            # Calculate the closeness centrality of the current node
            closeness[s] = total_reciprocal_distance / (N - 1)
        else:
            # Set the closeness centrality of the current node to 0
            closeness[s] = 0
    
    # Return the closeness centrality of each node
    return closeness

def find_reachable_nodes(G, source, time_attr): # Used for reachability_ratio calculation
    '''Function to find all nodes reachable from a source node in a graph.
    
       Input: G - the graph, source - the source node, time_attr - the attribute storing the time information.

       Output: A set of all nodes reachable from the source node.
    '''
    
    # Initialize an empty set to store the reachable nodes
    reachable = set()

    # Initialize a queue with the source node and the last time visited
    queue = deque([(source, -float('inf'))])

    # Initialize a set to keep track of visited nodes
    visited = set()
    
    # While there are nodes in the queue
    while queue:
        # Dequeue a node and the last time visited
        current, last_time = queue.popleft()
        
        # If the node has been visited at the same or a later time, skip it
        if (current, last_time) in visited:
            continue

        # Mark the node as visited at the current time
        visited.add((current, last_time))

        # Add the node to the set of reachable nodes
        reachable.add(current)
        
        # Get the neighbors of the current node
        neighbors = G.successors(current) if G.is_directed() else G.neighbors(current)
        
        # For each neighbor of the current node
        for neighbor in neighbors:
            # For each edge between the current node and the neighbor
            for key, edge_data in G[current][neighbor].items():
                # Get the time of the edge
                edge_time = edge_data[time_attr]

                # If the time is a datetime object, convert it to a timestamp
                if isinstance(edge_time, datetime):
                    edge_time = edge_time.timestamp()  # Convert Timestamp to seconds

                # If the time of the edge is later than the last time visited
                if edge_time > last_time:
                    # Enqueue the neighbor and the time of the edge
                    queue.append((neighbor, edge_time))
    
    # Return the set of reachable nodes
    return reachable

def calculate_reachability_ratio(G, time_attr):
    '''Function to calculate the reachability ratio of a graph.
    
       Input: G - the graph, time_attr - the attribute storing the time information.

       Output: The reachability ratio of the graph.
    '''
    
    # Get the total number of nodes in the graph
    total_nodes = len(G.nodes)
    
    # Calculate the total number of pairs of nodes
    total_pairs = total_nodes * (total_nodes - 1)
    
    # Initialize a counter for the number of reachable pairs of nodes
    reachable_pairs = 0
    
    # For each node in the graph
    for node in G.nodes:
        # Find all nodes reachable from the current node
        reachable_nodes = find_reachable_nodes(G, node, time_attr)
        
        # Add the number of reachable nodes (excluding the current node) to the counter
        reachable_pairs += len(reachable_nodes) - 1  # Exclude the node itself
    
    # Calculate the reachability ratio as the number of reachable pairs divided by the total number of pairs
    reachability_ratio = reachable_pairs / total_pairs
    
    # Return the reachability ratio
    return reachability_ratio

def reachability_latency(G, time_attr, r):
    '''Function to calculate the reachability latency of a graph.
    
       Input: G - the graph, time_attr - the attribute storing the time information, r - the fraction of nodes to consider (Reachability Ratio).

       Output: The reachability latency of the graph.
    '''
    
    # Get the total number of unique timestamps in the graph
    T = len(set(data[time_attr] for u, v, data in G.edges(data=True)))
    
    # Get the total number of nodes in the graph
    N = len(G.nodes)
    
    # Initialize a 2D array to store the average path length from each node at each time
    d_t_i = np.zeros((T, N))
    
    # For each unique timestamp
    for t, time in enumerate(sorted(set(data[time_attr] for u, v, data in G.edges(data=True)))):
        # For each node
        for i, node in enumerate(G.nodes):
            # Initialize a list to store the lengths of the shortest paths from the node to all other nodes
            path_lengths = []
            # For each target node
            for target in G.nodes:
                # If the node is not the target
                if node != target:
                    # Find the shortest paths from the node to the target
                    shortest_paths = find_temporal_shortest_paths(G, node, target, time_attr)
                    # If there are shortest paths
                    if shortest_paths:
                        # Add the length of the first shortest path to the list
                        path_lengths.append(len(shortest_paths[0]) - 1)
            # If there are path lengths
            if path_lengths:
                # Calculate the average path length and store it in the array
                d_t_i[t, i] = np.mean(path_lengths)
    
    # Calculate the number of nodes to consider
    k = int(np.floor(r * N))
    
    # Calculate the reachability latency as the average of the k shortest average path lengths at each time
    R_r = (1 / (T * N)) * np.sum(np.sort(d_t_i, axis=1)[:, k])
    
    # Return the reachability latency
    return R_r


    