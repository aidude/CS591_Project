# Dijkstra's algorithm for shortest paths
# This code has been utilized from following link

# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/117228
from priodict import priorityDictionary

def Dijkstra(G,start,end=None):
    """
    Find shortest paths from the start vertex to all
    vertices nearer than or equal to the end.


    @param G The graph dictionary to be searched
    @param start Starting node
    @param end End node
    @return Something important
    """

    D = {}  # dictionary of final distances
    P = {}  # dictionary of predecessors
    Q = priorityDictionary()   # est.dist. of non-final vert.
    Q[start] = 0

    for v in Q:
        D[v] = Q[v]
        if v == end: break

        for w in G[v]:
            vwLength = D[v] + G[v][w]
            if w in D:
                if vwLength < D[w]:
                    raise ValueError, \
  "Dijkstra: found better path to already-final vertex"
            elif w not in Q or vwLength < Q[w]:
                Q[w] = vwLength
                P[w] = v

    return (D,P)

def shortestPath(G,start,end):
    """
    Find a single shortest path from the given start vertex
    to the given end vertex.
    The input has the same conventions as Dijkstra().
    The output is a list of the vertices in order along
    the shortest path.
    @param G The graph dictionary to be searched
    @param start The starting node
    @param end The ending node
    @return A list of the nodes that lie on the shortest path
    from start to end in G
    """
    try:
        D,P = Dijkstra(G,start,end)
    except KeyError:
        return []
    Path = []
    while 1:
        Path.append(end)
        if end == start: break
        try:
            end = P[end]
        except KeyError:
            break
    Path.reverse()
    return Path
