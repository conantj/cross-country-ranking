import networkx as nx
import os
graph=nx.DiGraph()
nx.write_gpickle(graph,os.path.join(os.getcwd(),'Men','TimeGraph.gpickle'))
nx.write_gpickle(graph,os.path.join(os.getcwd(),'Men','WinsGraph.gpickle'))
nx.write_gpickle(graph,os.path.join(os.getcwd(),'Women','TimeGraph.gpickle'))
nx.write_gpickle(graph,os.path.join(os.getcwd(),'Women','WinsGraph.gpickle'))
