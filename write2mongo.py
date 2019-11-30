from config import MONGODB_CONFIG
import json
import pymongo


if __name__ == '__main__':
    fp = open('categories.json', 'r', encoding='utf-8')
    json_data = json.loads(fp.read())
    # mongo
    mongo = pymongo.MongoClient(host=MONGODB_CONFIG['ip'], port=MONGODB_CONFIG['port'])
    # 验证完成后切换库
    db = mongo['admin']
    db.authenticate(name=MONGODB_CONFIG['username'], password=MONGODB_CONFIG['password'])
    db = mongo['patent']
    # 专利数据集合
    collection = db['ipc_category']

    buffer = []
    counter = 0
    for datum in json_data:
        buffer.append(datum)

        if len(buffer) >= 1000:
            counter += len(buffer)
            collection.insert_many(buffer)
            buffer.clear()
            print('process:%d' % counter)
