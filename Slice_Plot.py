from matplotlib.patches import FancyArrowPatch
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

def slice_plot(G:nx, title:str, ylabel:str):

    # Extract edges from the graph
    temporal_edges = [(u, v, d['time']) for u, v, d in G.edges(data=True)]

    # Extract unique nodes and time points
    nodes = sorted(G.nodes())
    time_points = sorted(set(edge[2]['time'] for edge in G.edges(data=True)))

    # Create node positions
    node_positions = {node: i for i, node in enumerate(nodes)}
    time_positions = {time: i for i, time in enumerate(time_points)}

    # Initialize plot
    fig, ax = plt.subplots(figsize=(12, 8))

    # Draw nodes
    color_map = plt.cm.gray(np.linspace(0, 0.8, len(nodes)))
    for node, node_idx in node_positions.items():
        for time, time_idx in time_positions.items():
            ax.plot(time_idx, node_idx, 'o', color=color_map[node_idx], markersize=10)

    # Draw Bezier curves for edges
    for edge in temporal_edges:
        node1, node2, time = edge
        x1, y1 = time_positions[time], node_positions[node1]
        x2, y2 = time_positions[time], node_positions[node2]

        
        # Create the curve bending to the right
        control_point_1 = (x1 + 0.3, y1)
        control_point_2 = (x2 + 0.3, y2)
        verts = [(x1, y1), control_point_1, control_point_2, (x2, y2)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
        
        path = Path(verts, codes)

        if G.is_directed():
            patch = FancyArrowPatch(path=path, color='black', lw=1, arrowstyle='-|>', mutation_scale=25)
        else:
            patch = PathPatch(path, facecolor='none', edgecolor='black', lw=1)
        ax.add_patch(patch)

    # Customize plot
    ax.set_xlim(-1, len(time_points))
    ax.set_ylim(-1, len(nodes))
    ax.set_xticks(range(len(time_points)))
    if type(time_points[0]) == np.int64:
        ax.set_xticklabels([tp for tp in time_points])
    else:
        ax.set_xticklabels([tp.strftime('%Y-%m-%d') for tp in time_points])
    ax.set_title('{}'.format(title))
    ax.set_ylabel('{}'.format(ylabel))
    ax.set_xlabel('Time')
    ax.set_yticks(range(len(nodes)))
    ax.set_yticklabels(nodes)
    ax.grid(True)

    plt.show()
