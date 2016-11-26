from bs4 import BeautifulSoup
import urllib.request
import csv
import os
import re

#Retrieves Latest Results from TFRRS
#Returns list of [url, Meet Name]
def resultUrlPuller(url):  
	tfrrsUrl=urllib.request.urlopen(url)
	html=tfrrsUrl.read()
	wholePage=BeautifulSoup(html,'html.parser')
	
	results=wholePage.find('table',class_='data')
		
	resultsList=results.find_all('a')
	rList=[]
	
	for i in resultsList:
		rList.append(['http:'+i['href'].replace('.html','/'),i.string.replace('/','-').replace('"','')])
	return rList

#Takes a results url and returns Individual Results as lists	(Women followed by Men)
def resultFinder(url):
	tfrrsUrl=urllib.request.urlopen(url)
	html=tfrrsUrl.read()
	wholePage=BeautifulSoup(html,'html.parser')
	
	results=wholePage.find_all('div', string=perm)
	someThing=[]
	
	for i in results:
		temp=i.find_parent('table')
		someThing.append(temp)
	
	finalList={'women':[],'men':[], 'neither':[]}
	gender=genderCheck(wholePage)
	
	for index in range(len(someThing)):
		
		rest=someThing[index].find_all('tr')
		rList=[]
		for i in rest:
			temp=i.find_all('td')
			lst=[]
			for j in temp:
				k=j.stripped_strings
				for l in k:
					lst.append(l)
			if lst:
				rList.append(lst)
				
		finalList[gender[index]].append(rList)
	
	return finalList
#Search function for results in resultFinder
def perm(element):
	if element and "Place" in element.string:
		return True
	return False
#returns the gender of the results
def genderCheck(w):
	check=w.find_all('a', href=re.compile('#[0-9]+'),string=True)
	gender=[]
	for i in check:
		if 'Women' in i.string:
			gender.append('women')
			
		elif 'Men' in i.string:
			gender.append('men')
		else:	
			gender.append('neither')
	return gender

#Takes URLs of results and writes the results to a csv with the name of the meet	
def resultsWriter(resultUrls):
	mensPath=os.path.join(os.getcwd(),'Men')
	womensPath=os.path.join(os.getcwd(),'Women')
	
	for result in resultUrls:
		filename=result[1]+'.csv'
		
		if os.path.isfile(os.path.join(mensPath,filename)):
			continue
		
		results=resultFinder(result[0])
		if results['women']:
			counter=0
			for r in results['women']:
				if counter>0:
					with open(os.path.join(womensPath,result[1]+'_'+str(counter)+'.csv'),'w') as csvfile:
						writer=csv.writer(csvfile)
						for i in r:
							try:
								writer.writerow(i)
							except UnicodeEncodeError:
								pass
						csvfile.close()
				else:
					with open(os.path.join(womensPath,filename),'w') as csvfile:
						writer=csv.writer(csvfile)
						for i in r:
							try:
								writer.writerow(i)
							except UnicodeEncodeError:
								pass
						csvfile.close()
				counter+=1
		if results['men']:
			counter=0
			for r in results['men']:
				if counter>0:
					with open(os.path.join(mensPath,(result[1]+'_'+str(counter)+'.csv')),'w') as csvfile:
						writer=csv.writer(csvfile)
						for i in r:
							try:
								writer.writerow(i)
							except UnicodeEncodeError:
								pass
						csvfile.close()
				else:
					with open(os.path.join(mensPath,filename),'w') as csvfile:
						writer=csv.writer(csvfile)
						for i in r:
							try:
								writer.writerow(i)
							except UnicodeEncodeError:
								pass
						csvfile.close()
				counter+=1
		

resultsWriter(resultUrlPuller('http://tfrrs.org'))
