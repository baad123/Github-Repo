#!usr/bin/python
from flask import Flask, request, render_template
import requests
import json
from datetime import datetime, timedelta

app = Flask('Shipping assignment') 

# index template
@app.route('/')
def form():
    return render_template('index.html')


# fetch and display the number of issues
@app.route('/result/', methods=['POST'])
def result():
	#get the url to be fetched
	url=request.form['url']

	#filter the url
	urlsplit = url.split('/')
	if len(urlsplit) ==6 and urlsplit[5] == 'issues' and 'issues' in urlsplit:
		url = 'https://api.github.com/repos/' + urlsplit[3] + '/' + urlsplit[4]
		urlToIssues = 'https://api.github.com/repos/' + urlsplit[3] + '/' + urlsplit[4] + '/' + urlsplit[5] + '?state=open&page='
	elif len(urlsplit) == 5 and 'issues' not in urlsplit:
		url = 'https://api.github.com/repos/' + urlsplit[3] + '/' + urlsplit[4]
		urlToIssues = 'https://api.github.com/repos/' + urlsplit[3] + '/' + urlsplit[4] + '/issues?state=open&page='


	date_o = []				#list to hold all date objects
	dates = []				#list to hold all timestamps extracted

	#get last24hrs timestamp
	last24hrs = datetime.now() - timedelta(days=1)

	#get last7days timestamp	
	last7days = datetime.now() - timedelta(days=7)

	#get last30days timestamp		
	last30days = datetime.now() - timedelta(days=30)

	#initalize count 
	count = count1 = 0

	try:
		r = requests.get(url,auth=('username', 'pass'))
		print r
		if(r.ok):
			repoItem = json.loads(r.text or r.content)
			#get no of open issues
			open_issues = repoItem['open_issues']
			
			#calculate no of pages as ony 30 results are returned per page
			noOfPages = float(open_issues)/30
			intNoOfpages = int(noOfPages)
			if noOfPages > intNoOfpages:
				noOfPages = intNoOfpages+1
			elif noOfPages == intNoOfpages:
				noOfPages = intNoOfpages
			
			#request reach page one by one 
			for i in range(1,noOfPages+1):
				pr = requests.get(urlToIssues + str(i),auth=('username', 'pass'))
				res = json.loads(pr.text or pr.content)

				#get timestamp for each issue and append it to list 
				for i in range(len(res)):
					dates.append(str(res[i]['created_at'].replace("T", " ").replace("Z", " ")))
		

		# convert each timestamp into date object
		for i in range(len(dates)):
			date_object = datetime.strptime(dates[i][:-1], '%Y-%m-%d %H:%M:%S')
			date_o.append(date_object)

		#for every date in date_o list check the range
		for date in date_o:
			#check if the date is within 24 hours
			if date > last24hrs:
				count = count + 1
				#print date, last24hrs
			if date < last24hrs and date > last7days:
				count1 = count1 + 1
						 
		#only string can be returned hence sonvert them to string
		within24 = str(count)
		within7 = str(count1)
		after7 = str(open_issues - count1 - count)

		return render_template('result.html', issuesOpen=open_issues,within24 = within24,within7 = within7, after7 = after7)
	except:
		return render_template('error.html')


if __name__=='__main__':
	app.run(debug=True,host='0.0.0.0')
