import re

text = ""
with open('./test.txt', 'r', encoding='utf-8') as f:
    text = f.read()

content = re.search(r"<div class=\"caas-body\">.*</div>", text)
print(content)