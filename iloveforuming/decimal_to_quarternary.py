while True:
    num=input("gimme a number: ")
    try:
        num=int(num)
    except:
        continue
    c=bin(num)[2:]
    if len(c)%2==0:
        c="0"+c
    
    #print(c)
    for i in range(0,len(c)-1,2):
        #print(c[i],c[i+1])
        print((c[i]=="1")*2+(c[i+1]=="1"),end="")
    print()