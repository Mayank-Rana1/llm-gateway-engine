# class AI:
#     def __init__(self, api_key):
#         self.api_key = api_key
#         self.base_url = "https://api.openai.com"
    
#     def api_key(self):
#         return self.api_key

# client = AI("sk-12354Mayank")
# x=client.api_key()
# print(x)
# print(("#"*3+"\n")*3,end="")

while 1:
    x=input().strip()
    if "@" not in x or "." not in x:
        print("invalid")
    elif x.split("@")[0] and x.split("@")[1].split(".")[0] and x.split("@")[1].split(".")[1]:
        print("Valid")
    else:
        print("Invalid")