import WeightedGraph
import Dijstra
g = WeightedGraph.WeightedGraph("graph.txt")
dis = Dijstra.Dijstra(g, 0)
for v in range(g.V):
    print(dis.dis_to(v), " ")