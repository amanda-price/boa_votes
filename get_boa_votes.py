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
		if line.startswith("Board Bill No."):
			row = line.split()
			bb = row[3]
			print(year,bb)
		#print(":: {}".format(line))
		if line.startswith("Your feedback was not sent"):
			writeOnFlag =False

		if writeOnFlag:
			row = line.strip()
			if not line.startswith("Alderman") and not noVoteFlag:
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
						vote_file.write("{},{},{},{}\n".format(bb,ward,alderperson,voteType))
					count = count -1
					
				#print(row)
		
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
				count = numberOfVotes*2
				noVoteFlag = False


bblist = []
years = ["2018-2019","2017-2018","2016-2017","2015-2016"]
#years = ["2016-2017","2015-2016"]

for year in years:
	vote_file = open("boa_votes_"+year[2:4]+year[-2:]+".csv",'w')
	vote_file.write("bbid,ward,alderperson,vote\n")
	url = "https://www.stlouis-mo.gov/government/city-laws/board-bills/votes/index.cfm?session="+year+"&submit=Choose+Session"
	response = urllib.request.urlopen(url)
	soup = BeautifulSoup(response.read(), 'html.parser')

	for link in soup.findAll('a', attrs={'href': re.compile("board-bill.cfm")}):
		url_string = link.get('href')
		if not url_string[-5] == "#":
			bblist.append(link.get('href'))

	for bbid in bblist:
		getVotes(bbid)