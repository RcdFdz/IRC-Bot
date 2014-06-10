import hashlib
import json
import os
import csv

def loadUsersFromFile():
  usersDict = {}

  if not os.path.isfile('.users'):
    file = open('.users', 'w')
    print>> file, "admin\tee9f678de6171df4d90b6d772d94b79f0915f57c"
    file.close()

  with open('.users', 'r') as file:
    reader = csv.reader(file, delimiter="\t")
    for row in reader:
      usersDict[row[0]] =  row[1]
  file.close()

  return usersDict

def writeToUsersFile(content):
  with open('.users', 'w') as file:
    writer = csv.writer(file, delimiter="\t")
    for key, value in content.items():
      writer.writerow([key, value])
  file.close()

def isUserRegistred(user):
  usersData = loadUsersFromFile()

  return (user in usersData)

def register(user, passwd):
  isRegistred = isUserRegistred(user)

  if not isRegistred:
    usersFile = loadUsersFromFile()
    passCoded = hashlib.sha1(passwd).hexdigest()

    usersFile[user] = passCoded
    writeToUsersFile(usersFile)
    return True
  else:
    return False

def identify(user, passwd):
  usersFile = loadUsersFromFile()
  if isUserRegistred(user):
    return usersFile[user] == hashlib.sha1(passwd).hexdigest()
  else:
    return False

if __name__ == "__main__":
  main()
