import csv
import requests
import time

IPT_URL             = 'http://ipt-inpn.gbif.fr/'
IPT_USER            = ''
IPT_PWD             = ''
UUID_FILE           = '/workspace/ipt-batch-import-inpn/uuid'

uidList = []

def publishAll():
    session = __login()
    for uid in uidList:
        publish(uid, session)

def registerAll():
    session = __login()
    for uid in uidList:
        register(uid, session)

def publish(dr, session):
    print("Publish "+dr)
    data = {"r": dr, "currPubMode": "AUTO_PUBLISH_OFF", "publish": "Publish"}
    responsePublish = session.post(IPT_URL + 'manage/publish.do', data=data)
    if responsePublish.status_code == 200:
        while True:
            responseReport = session.get(IPT_URL + 'manage/report.do?r='+dr)
            if responseReport.status_code == 200:
                print ("waiting...")
                if ("<divclass=\"completed\">" in responseReport.text):
                    return
                time.sleep(0.5)
            else:
                return

def register(dr, session):
    print("Register "+dr)
    data = {"r": dr, "register": "Register"}
    responseRegister = session.post(IPT_URL + 'manage/resource-registerResource.do', data=data)
    print(responseRegister)

def __login():
    session = requests.Session()
    session.post(IPT_URL)
    data = {"email": IPT_USER, "password": IPT_PWD, "csrfToken": session.cookies['CSRFtoken'], "portal.login": "login"}
    session.post(IPT_URL + 'login.do', data=data)
    return session

if __name__ == "__main__":
    print("Automate...")

    print("Read UUID file: "+UUID_FILE)
    with open(UUID_FILE, newline='') as csvfile:
        csv_reader = csv.reader(csvfile, delimiter=';')
        csv_rows = list(csv_reader)
        for row in csv_rows:
            uidList.append(row[0])

    for uid in uidList:
        print(uid)

    #publishAll()
    #registerAll()
