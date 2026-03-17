path = 'C:/Users/HeitorDanielS/Downloads/FloppaAI/desktop/index.html'
with open(path,'r',encoding='utf-8') as f: c = f.read()

# Fix BUG_REPORT instrucao
c = c.replace(
    "BUG REPORT: apos investigar, inicie com",
    "BUG REPORT: SOMENTE use"
)
c = c.replace(
    "BUG_REPORT: [resumo] e continue.",
    "BUG_REPORT:[sumario_detalhado] quando JA TEM informacoes suficientes (2+ respostas do usuario). Sumario deve ter 10+ chars e ser especifico."
)

# Fix ticket options
c = c.replace(
    '<option value="bug">🐛 Bug</option>\n          <option value="duvida">❓ Dúvida</option>\n          <option value="sugestao">💡 Sugestão</option>',
    '<option value="bug">🐛 Bug</option>\n          <option value="ideia">💡 Ideia / Sugestão</option>\n          <option value="duvida">❓ Dúvida</option>'
)

# Fix slbl
c = c.replace("duvida:\"❓ Dúvida\",sugestao:\"💡 Sugestão\"", "ideia:\"💡 Ideia\",duvida:\"❓ Dúvida\"")

# Add user_id to ticket
c = c.replace(
    "{id:genId(),date:nowStr(),name,subject:sub,message:msg,response:\"\",platform:\"pc\"}",
    "{id:genId(),date:nowStr(),name,subject:sub,message:msg,response:\"\",platform:\"pc\",user_id:USER_ID||\"\"}"
)

# Add USER_ID var
c = c.replace("let USERNAME=\"\", IS_DEV=false,", "let USERNAME=\"\", USER_ID=\"\", IS_DEV=false,")

# Fix BUG_REPORT detection in sendChat
old_bug = '''if(reply.startsWith("🐛BUG_REPORT:")){
      const[l,...rest]=reply.split("\\n");registerBug(l.replace("🐛BUG_REPORT:","").trim());reply=rest.join("\\n").trim();
    }'''
new_bug = '''const bugMatch=reply.match(/^BUG_REPORT:(.+)/m);
    if(bugMatch){
      const summary=bugMatch[1].trim();
      if(summary.length>=10){
        reply=reply.replace(/^BUG_REPORT:.+\\n?/m,"").trim();
        registerBug(summary);
      } else {
        reply=reply.replace(/^BUG_REPORT:.+\\n?/m,"").trim();
      }
    }'''
c = c.replace(old_bug, new_bug)

with open(path,'w',encoding='utf-8') as f: f.write(c)
print('desktop OK')
