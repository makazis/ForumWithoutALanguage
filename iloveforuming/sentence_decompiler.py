sentences=[]
with open("sentence_ideas.txt","r") as f:
    for i in f.read().split("\n"):
        sentences.append(" ".join(i.split(" ")[1:]))
print(sentences)

