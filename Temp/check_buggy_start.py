import pymongo
from bson import ObjectId



from Utils.IOHelper import readF2L

ids_f="D:\DDPR\Dataset\\freq50_611\\trn_ids.txt"
ids = readF2L(ids_f)
mongoClient = pymongo.MongoClient("mongodb://localhost:27017/")
db=mongoClient["BF_Methods"]
bug_col = db["Buginfo"]
startset=set()
for index,id in enumerate(ids):

    bug = bug_col.find_one({"_id": ObjectId(id)})
    if bug==None:
        continue
    buggycode=bug['buggy_code'].split('\n')
    print(index)
    max_count=0
    for line in buggycode:
        line=line.strip()
        if line =="":
            continue
        if not line[0].isalpha():
            print(line)
            max_count+=1
        else:
            startset.add(max_count)
            break
print(startset)
