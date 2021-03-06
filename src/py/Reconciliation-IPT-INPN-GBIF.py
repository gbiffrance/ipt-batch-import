import csv
import requests

GBIF_FILE = "output/GBIF-2020-09-01.csv"
IPT_FILE = "output/IPT_2020-09-01.csv"
RECONCIL_FILE = "output/reconcil-2020-09-01.csv"

# Generate GBIF_FILE from GBIF API
def getPatrinatDatasetGBIF():
    urlGBIF = 'http://api.gbif.org/v1/organization/1928bdf0-f5d2-11dc-8c12-b8a03c50a862/publishedDataset'

    out = open(GBIF_FILE, "w")
    out.write("UID_GBIF")
    out.write(";")
    out.write("UID_IPT")
    out.write(";")
    out.write("TITLE")
    out.write(";")
    out.write("CREATED_DATE")
    out.write(";")
    out.write("MODIFIED_DATE")
    out.write(";")
    out.write("COUNT_GBIF")
    out.write(";")
    out.write("URL_IPT")
    out.write("\n")

    check = []

    offset = 0
    limit = 10
    i = 1
    while True:
        urlComplete = urlGBIF+'?limit='+str(limit)+'&offset='+str(offset)
        print(urlComplete)
        response = requests.get(urlComplete)
        data = response.json()

        for r in data['results']:
            key = ""
            created = ""
            modified = ""
            recordCount = -1
            title = ""
            iptId = ""
            url = ""

            key = r['key']

            if (key in check):
                print("ERROR "+key)
                return

            check.append(key)

            print(str(i) + " / " +key)
            i = i + 1

            title = r['title']

            responseDetail = requests.get('http://api.gbif.org/v1/dataset/'+key)
            dataDetail = responseDetail.json()
            created = dataDetail['created']
            modified = dataDetail['modified']

            foundIdentifier = False
            for identifier in dataDetail['identifiers']:
                if (identifier['type'] == "URL"):
                    url = identifier['identifier']
                    foundIdentifier = True
                    break

            if (foundIdentifier == False):
                responseEndpoint = requests.get('http://api.gbif.org/v1/dataset/'+key+'/endpoint')
                dataEndpoint = responseEndpoint.json()
                for endpoint in dataEndpoint:
                    if ((endpoint['type'] == "DWC_ARCHIVE") or (endpoint['type'] == "EML")):
                        url = endpoint['url']
                        break

            responseCount = requests.get('http://api.gbif.org/v1/occurrence/count?datasetKey='+key)
            recordCount = responseCount.text

            iptId = url[(url.rfind('=')+1)::]
            out.write(key+";"+iptId+";"+title+";"+created+";"+modified+";"+str(recordCount)+";"+url+"\n")

        if data['endOfRecords']:
            break
        else:
            offset = offset + limit

    out.close()

# Generate RECONCIL_FILE by reconciliating IPT_FILE and GBIF_FILE
def reconcil():
    out = open(RECONCIL_FILE, "w")
    out.write("UID_GBIF")
    out.write(";")
    out.write("TITLE")
    out.write(";")
    out.write("CREATED_DATE")
    out.write(";")
    out.write("MODIFIED_DATE")
    out.write(";")
    out.write("STATUS_GBIF")
    out.write(";")
    out.write("COUNT_GBIF")
    out.write(";")
    out.write("UID_IPT")
    out.write(";")
    out.write("URL_IPT")
    out.write(";")
    out.write("COUNT_IPT")
    out.write(";")
    out.write("DIFF")
    out.write("\n")

    uidList = {}
    with open(IPT_FILE, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';')
        csv_rows = list(csv_reader)[1:]

        for row in csv_rows:
            uidList[row[0]] = row[2]

    drFound = []

    with open(GBIF_FILE, newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=';')
            csv_rows = list(csv_reader)

            for row in csv_rows:
                id = row[1]
                count = ""
                diff = ""
                if (id in uidList):
                    action = "FOUND"
                    count = int(uidList[id])
                    diff = int(count) - int(row[4])
                    drFound.append(id)
                    out.write(row[0]+";"+row[1]+";"+row[2]+";"+row[3]+";"+row[4]+";"+action+";"+row[5]+";"+row[6]+";"+str(count)+";"+str(diff)+"\n")
                else:
                    out.write(row[0]+";"+row[1]+";"+row[2]+";"+row[3]+";"+row[4]+";NOT FOUND;"+row[5]+";"+row[6]+";;\n")

            for id in uidList:
                if (id not in drFound):
                    count = int(uidList[id])
                    out.write(";"+id+";;;;NOT_FOUND;;;"+str(count)+";\n")

    out.close()

def main():
    getPatrinatDatasetGBIF()
    #reconcil()

if __name__ == "__main__":
    main()
