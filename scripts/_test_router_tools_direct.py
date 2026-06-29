import json, urllib.request
body={
 'model':'gpt-3.5-turbo','stream':False,
 'messages':[{'role':'user','content':'Use update_todo_list to add todo Test'}],
 'tools':[{'type':'function','function':{'name':'update_todo_list','description':'Update todos','parameters':{'type':'object','properties':{'todos':{'type':'string'}},'required':['todos']}}}],
 'tool_choice':'required'
}
req=urllib.request.Request('http://127.0.0.1:8001/v1/chat/completions',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
r=urllib.request.urlopen(req,timeout=120)
d=json.loads(r.read())
print('model used:', d.get('model'))
msg=d['choices'][0]['message']
print('tool_calls:', msg.get('tool_calls'))
print('content:', (msg.get('content') or '')[:200])
