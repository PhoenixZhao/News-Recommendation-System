#coding=utf8
'''
    使用xapian将训练集建立索引，索引的域包括: title，content，timestamp，newsid
    调用jieba进行分词，并去掉停用词
'''
import os
import json
import xapian

data_dir = '/Users/huanzhao/projects/recommendation-system-contest/data/splited_data/'
train_data_path = data_dir + 'train_data_unique_nid.txt'
index_file_path = data_dir + 'index_file'

def parse_train_data(train_data_path):
    '''
        读入已经分词和消重后的训练集，生成待索引数据的list，每一个都是一个dict,
        key=index_name, value=index_text
        训练集中的title和content已经进行分词,并去掉停用词，所以直接读取即可
    '''
    f = open(train_data_path, 'r')
    line = f.readline()
    index_records = []

    cnt = 0
    while line:
        cnt += 1
        #if cnt == 10:
        #    break
        record = {}
        parts = line.strip().split('\t\t')

        record['title'] = parts[3]
        record['content'] = parts[4]
        record['ts'] = parts[2]
        record['newsid'] = parts[1]
        index_records.append(record)

        line = f.readline()

    print 'finish loading %s index records' % (cnt)

    return index_records

def index(index_file_path):
    print 'run index...'

    if os.path.isdir(index_file_path):
        os.system('rm -rf %s' % (index_file_path))

    # Create or open the database we're going to be writing to.
    db = xapian.WritableDatabase(index_file_path, xapian.DB_CREATE_OR_OPEN)

    # Set up a TermGenerator that we'll use in indexing.
    termgenerator = xapian.TermGenerator()
    #termgenerator.set_stemmer(xapian.Stem("en"))

    cnt = 0
    index_records = parse_train_data(train_data_path)
    for fields in index_records:
        cnt += 1
        if cnt % 1000 == 0:
            print 'finish %s articles' % str(cnt)


        content = fields.get('content', u'')
        title = fields.get('title', u'')
        timestamp = fields.get('ts', u'')#timestamp
        newsid = fields.get('newsid', u'')

        # We make a document and tell the term generator to use this.
        doc = xapian.Document()
        termgenerator.set_document(doc)

        # Index each field with a suitable prefix.
        termgenerator.index_text(title, 1, 'tt')
        termgenerator.index_text(content, 1, 'cn')
        termgenerator.index_text(newsid, 1, 'nid')
        termgenerator.index_text(timestamp, 1, 'ts')

        # Store all the fields for display purposes.
        doc.set_data(json.dumps(fields, encoding='utf8'))

        db.add_document(doc)

        # We use the identifier to ensure each object ends up in the
        # database only once no matter how many times we run the
        # indexer.
        #idterm = u"Q" + newsid
        #doc.add_boolean_term(idterm)
        #db.replace_document(idterm, doc)
    print 'finish indexing %s articles!' % cnt


def main():
    index(index_file_path)

if __name__ == '__main__':
    main()
