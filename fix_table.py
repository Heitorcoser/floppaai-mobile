import sys
for f in ['mobile','desktop']:
    path = 'C:/Users/HeitorDanielS/Downloads/FloppaAI/'+f+'/index.html'
    with open(path,'r',encoding='utf-8') as fp:
        c = fp.read()
    count = c.count('"messages"')
    c2 = c.replace('"messages"', '"chat_messages"')
    with open(path,'w',encoding='utf-8') as fp:
        fp.write(c2)
    print(f, count, 'trocas')
