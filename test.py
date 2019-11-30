import pymongo
from config import MONGODB_CONFIG


if __name__ == '__main__':
    # mongo
    mongo = pymongo.MongoClient(host=MONGODB_CONFIG['ip'], port=MONGODB_CONFIG['port'])
    # 验证完成后切换库
    db = mongo['admin']
    db.authenticate(name=MONGODB_CONFIG['username'], password=MONGODB_CONFIG['password'])
    db = mongo['patent']
    # 专利数据集合
    collection = db['ipc_category']
    # 查找
    cls_number = 'H05G1/02'
    result = collection.find_one({'code': cls_number})
    ipc_texts = [ancestor['title'] for ancestor in result['ancestors']]

    print('、'.join(ipc_texts))

