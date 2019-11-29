from config import MONGODB_CONFIG
import json
import pymongo


def browse_tree(root):
    stack = [root]
    array = []

    while len(stack) != 0:
        top = stack[0]
        stack.pop(0)
        datum = {'code': top['code'], 'title': top['title'], 'children': []}

        for child in top['children']:
            datum['children'].append(child['code'])
            stack.append(child)

        if len(datum['children']) == 0:
            del datum['children']
        array.append(datum)
    return array


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
    collection = db['hownet_category']

    for root in json_data:
        items = browse_tree(root)
        print(items)
        # collection.insert_many(items)