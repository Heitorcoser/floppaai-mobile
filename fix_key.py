OLD_KEY = "sb_publishable_nLx32tzEkLUyXe3J4YfHKg_apSpDoI0"
OLD_URL = "https://gxjmolabyaiuuwvioyuw.supabase.co"
NEW_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtsY2Rna3N5ZGRseWZhem93aGViIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM2MzAwMTAsImV4cCI6MjA4OTIwNjAxMH0.pYqDAbpYWvnr0sf2pQJ5BBx1dAU9HUX2Amd69RWvSSg"
NEW_URL = "https://klcdgksyddlyfazowheb.supabase.co"

for f in ['mobile','desktop']:
    path = 'C:/Users/HeitorDanielS/Downloads/FloppaAI/'+f+'/index.html'
    with open(path,'r',encoding='utf-8') as fp:
        c = fp.read()
    c2 = c.replace(OLD_KEY, NEW_KEY).replace(OLD_URL, NEW_URL)
    with open(path,'w',encoding='utf-8') as fp:
        fp.write(c2)
    print(f, 'OK - key:', OLD_KEY[:15]+'... ->', NEW_KEY[:20]+'...')
    print(f, 'OK - url:', OLD_URL, '->', NEW_URL)
