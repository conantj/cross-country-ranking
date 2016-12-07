import csv
import os
import networkx as nx
import numpy
import re

#Updates the list of athletes used to generate nodes on the graph
def updateAthleteList(path,results):
	athletes=[]
	path=os.path.join(path,'AthleteList.csv')
	
	with open(path,'r') as csvfile:
		reader=csv.reader(csvfile)
		for row in reader:
			athletes.append(row)
		csvfile.close()
	athleteZip=list(map(list, zip(*athletes)))
	orLen=len(athletes)
	for row in results:
		
		name=row['Name']
		
		try:
			index=athleteZip[0].index(name)
			
		except ValueError:
			athletes.append([name,row['Team'],row['Year']])
			row[0]=len(athletes)-1
		else:
			if athleteZip[1][index]!=row['Team']:
				athletes.append([name,row['Team'],row['Year']])
				row[0]=len(athletes)-1
			else:
				row['Place']=index
				if athletes[index][2]=='':
					athletes[index][2]=row['Year']
	
	if orLen<len(athletes):
		
		with open(path,'a',newline='') as csvfile:
		
			writer=csv.writer(csvfile)
			writer.writerows(athletes[orLen:])
			csvfile.close()
	
	return athletes, results

	
def updateTimeGraph(results,athletes,graph=None,save=True):
	if graph==None:
		graph=nx.read_gpickle(os.path.join(os.getcwd(),'TimeGraph.gpickle'))
	m=len(graph)
	n=len(athletes)
	while(m<n):
		graph.add_node(m,name=athletes[m][0],school=athletes[m][1],grade=athletes[m][2])
		m=m+1
	for i in range(len(results)):
		for j in range(i+1,len(results)):
			jNode=results[j]['Place']
			iNode=results[i]['Place']
			if graph.has_edge(jNode,iNode):
				graph[jNode][iNode]['races']+=1
				graph[jNode][iNode]['weight']=(graph[jNode][iNode]['weight']*(graph[jNode][iNode]['races']-1)+results[j]['Time']-results[i]['Time'])/graph[jNode][iNode]['races']
			else:	
				graph.add_edge(jNode,iNode,weight=results[j]['Time']-results[i]['Time'],races=1)
	if save:
		nx.write_gpickle(graph,os.path.join(os.getcwd(),'TimeGraph.gpickle'))
	return graph

def updateWinsGraph(results,athletes,graph=None,save=True):
	if graph==None:
		graph=nx.read_gpickle(os.path.join(os.getcwd(),'WinsGraph.gpickle'))
	m=len(graph)
	n=len(athletes)
	while(m<n):
		graph.add_node(m,name=athletes[m][0],school=athletes[m][1],grade=athletes[m][2])
		m=m+1
	for i in range(len(results)):
		for j in range(i+1,len(results)):
			jNode=results[j]['Place']
			iNode=results[i]['Place']
			if graph.has_edge(jNode,iNode):
				graph[jNode][iNode]['weight']=graph[jNode][iNode]['weight']+1
			else:
				graph.add_edge(jNode,iNode,weight=1)
	if save:
		nx.write_gpickle(graph,os.path.join(os.getcwd(),'WinsGraph.gpickle'))
	return graph

def loadSchoolsFile():
	
	with open('schools.csv','rb') as csvfile:
		reader=csv.reader(csvfile)
		for row in reader:
			schools=row
		csvfile.close()
	return schools


def updateGraphs(path=os.getcwd(),rtn=False):
	path1=os.path.join(path,'NewResults')
	path2=os.path.join(path,'ArchivedResults')

	
	
	timeGraph=nx.read_gpickle(os.path.join(path,'TimeGraph.gpickle'))
	winsGraph=nx.read_gpickle(os.path.join(path,'WinsGraph.gpickle'))
	
	
	for filename in os.listdir(path1):
		#results will be a list of dictionaries with keyes 
		#ID, NAME(or FIRST_NAME, LAST_NAME), SCHOOL, GRADE, and TIME
		result=[] 
		print(filename)
		with open(os.path.join(path1,filename),'r') as csvfile:
			reader=csv.DictReader(csvfile)
			for row in reader:
				if not re.match('[1-5][0-9]:[0-5][0-9]',row['Time']):
					continue
				time=[float(y) for y in row['Time'].split(':')]  #Convert the time to seconds
				row['Time']=time[0]*60+time[1]
				result.append(row)    #Add to results
			csvfile.close()
		
		os.rename(os.path.join(path1,filename),os.path.join(path2,filename))
		athletes,result=updateAthleteList(path,result)
		updateTimeGraph(result,athletes,timeGraph,False)
		updateWinsGraph(result,athletes,winsGraph,False)
	
	nx.write_gpickle(winsGraph,os.path.join(path,'WinsGraph.gpickle'))
	nx.write_gpickle(timeGraph,os.path.join(path,'TimeGraph.gpickle'))
	if rtn:
		return timeGraph, winsGraph
	#

def getRanking(graph):
	matrix=nx.to_numpy_matrix(graph)
	matrix=matrix+.1
	lenM=len(matrix)
	rowSums=matrix.sum(1)
	stochasticMatrix=numpy.matrix(numpy.zeros((lenM,lenM)))
	for i in range(lenM):
		stochasticMatrix[i]=matrix[i]/rowSums[i]
	vector=numpy.matrix(numpy.ones((1,lenM)))
	prevVect=numpy.matrix(numpy.zeros((1,lenM)))
	while abs(vector-prevVect).sum()>.000001:
		prevVect=vector
		vector=vector*stochasticMatrix
	nodes=graph.nodes(data=True)
	nodeTuples=[]
	for i in range(lenM):
		try:
			nodeTuples.append((vector.item(nodes[i][0]),nodes[i][1]['name'],nodes[i][1]['school'],nodes[i][1]['grade']))
		except (TypeError,KeyError):
			print(nodes[i])
	dtype=[('value',float),('name','S25'),('school','S25'),('grade','S4')]
	ranking=numpy.array(nodeTuples,dtype=dtype)
	return numpy.sort(ranking, order='value')
	
def rankRunners(path=os.getcwd()):
	timeGraph,winsGraph=updateGraphs(path,True)
	timeRank=getRanking(timeGraph)
	winsRank=getRanking(winsGraph)
	with open(os.path.join(path,'timeRanking.csv'),'w') as csvfile:
		writer=csv.writer(csvfile)
		writer.writerows(timeRank)
	with open(os.path.join(path,'winsRanking.csv'),'w') as csvfile:
		writer=csv.writer(csvfile)
		writer.writerows(winsRank)
rankRunners(os.path.join(os.getcwd(),'Men'))
rankRunners(os.path.join(os.getcwd(),'Women'))