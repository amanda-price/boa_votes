from bs4 import BeautifulSoup
import urllib
import re

def getVotes(bbid):
	url = "https://www.stlouis-mo.gov/government/city-laws/board-bills/votes/"+bbid
	response = urllib.request.urlopen(url)
	soup = BeautifulSoup(response.read(), 'html.parser')
	text = soup.get_text().splitlines()

	writeOnFlag = False
	noVoteFlag = False

	voteTypes = ("Ayes","Noes","Did Not Vote","Abstain","Present","Absent","Vacant Seat")

	for line in text:
		if line.startswith(year+" Board bill"):
			row = line.split("--")
			description = row[1].strip().replace(",","")
		if line.startswith("Board Bill No."):
			row = line.split()
			bb = row[3]
		if line.startswith("Your feedback was not sent"):
			writeOnFlag =False
		if "/20" in line:
			date = line
		if writeOnFlag:
			row = line.strip()
			if not line.startswith("Alderman") and not noVoteFlag:
				## We could ignore everything beginning with "Ward" but if the ward is vacant, theres a "Ward XX Vacant"
				## listing in the absent section. 
				if line.startswith("Ward") and not line.endswith("Vacant"):
					continue
				if not row == "":
					if count%2 == 0:
						ward = line.strip()
					else: 
						alderperson = line.strip()
						if voteType == "Ayes":
							voteType = "Aye"
						if voteType == "Noes":
							voteType = "No"
						if description == "":
							print("Description not saved")
						unique_id = year+"-"+bb
						vote_file.write("{},{},{},{},{},{}\n".format(unique_id,year,bb,ward,alderperson,voteType))
						
					count = count -1

		if line.startswith(voteTypes):
			for elem in voteTypes:
				if line.startswith(elem):
					voteType = elem
			row = line.split(" ")
			row[-1] = row[-1].replace("(","")
			row[-1] = row[-1].replace(")","")
			numberOfVotes = int(row[-1])
			writeOnFlag = True
			if numberOfVotes == 0:
				noVoteFlag = True
			else:
				## We need the count multiplied by two, to parse for each ward/alderperson combo. There probably is 
				## a better way to do this, but it works.
				count = numberOfVotes*2
				noVoteFlag = False
	id_num = bbid.split("=")
	url2 = "https://www.stlouis-mo.gov/government/city-laws/board-bills/boardbill.cfm?bbDetail=true&BBId="+id_num[1]
	try:
		response = urllib.request.urlopen(url2)
	except:
		print(url2)
	soup = BeautifulSoup(response.read(), 'html.parser')
	text = soup.get_text().splitlines()
	sponsorFlag = False
	sponsor = "n/a"
	for line in text:
		if sponsorFlag:
			sponsor = line.strip()
			sponsorFlag = False
		if line.startswith("Sponsor:"):
			sponsorFlag = True
	print(year,bb,description)

	bb_file.write("{},{},{},{},{},{},{}\n".format(unique_id,year,bb,sponsor,date,description,url))



## These are the years shown currently. Once the 19/20 session starts, this could be replaced just to parse that 
## new session.
years = ["2018-2019","2017-2018","2016-2017","2015-2016"]


for year in years:
	bblist = []
	## Separating the BOA votes into files by session
	vote_file = open("boa_votes_"+year[2:4]+year[-2:]+".csv",'w')
	bb_file = open("boa_bb_"+year[2:4]+year[-2:]+".csv",'w')
	## bbid is the Board Bill number
	vote_file.write("unique_id,session,bbid,ward,alderperson,vote\n")
	bb_file.write("unique_id,session,bbid,sponsor,date of vote, title, url\n")

	url = "https://www.stlouis-mo.gov/government/city-laws/board-bills/votes/index.cfm?session="+year+"&submit=Choose+Session"
	response = urllib.request.urlopen(url)
	soup = BeautifulSoup(response.read(), 'html.parser')

	## Unfortunately,the links are not tied to the exact board bill number (but man it would have been great if 
	## they were). Instead, we need to parse the page for the links to the new pages
	for link in soup.findAll('a', attrs={'href': re.compile("board-bill.cfm")}):
		url_string = link.get('href')
		if not url_string[-5] == "#": ## Ignore the links to the Aye and Nay votes, we want the full page
			bblist.append(link.get('href'))

	for bbid in bblist:
		getVotes(bbid)
		
	vote_file.close()