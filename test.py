H=25056.2
L=25038.9


# buy
bt1=((H+L)/2)+  ((H-L)+(0.618*(H-L)))
bt2= (((H+L)/2) + ((H-L)+(0.618*(H-L)))) + (H-L)
bsl= ((H+L)/2)-3

print("bt1: ",bt1)
print("bt2: ",bt2)
print("bsl: ",bsl)

# # sell
st1=((H+L)/2)- ((H-L)+(0.618*(H-L)))
st2=((H+L)/2) - ((H-L)+(0.618*(H-L)))- (H-L)

print("st1: ",st1)
print("st2: ",st2)

buytsl= (((H+L)/2)+(H-L)+(0.618*(H-L))) -  (H-L)
print("buytsl: ",buytsl)
selltsl=((H+L)/2)-((H-L)+(0.618*(H-L)))+   (H-L)
print("selltsl: ",selltsl)


buyreversal= (((H+L)/2)+(H-L)+(0.618*(H-L))) + ((H-L)+(0.618*(H-L)))
print("buyreversal: ",buyreversal)


test=(((H+L)/2)-(H-L)+(0.618*(H-L)))-((H-L)+(0.618*(H-L)))
exp1= (((H+L)/2)-(H-L)+(0.618*(H-L)))
exp2=  ((H-L)+(0.618*(H-L)))


newformula= (H-L)+(0.618*(H-L))
sellreversal = ((H+L)/2)- ((H-L)+(0.618*(H-L))) -  ((H-L)+(0.618*(H-L)))
print("sellreversal: ",sellreversal)

brt1= ((H+L)/2)+  ((H-L)+(0.618*(H-L)))  + (H-L)
print("brt1: ",brt1)

brt2= ((H+L)/2)+ (H-L)+(0.618*(H-L))
print("brt2: ",brt2)

brsl=  (((H+L)/2)+(H-L)+(0.618*(H-L))) + ((H-L)+(0.618*(H-L))) + 3
print("brsl: ",brsl)

srt1= ((H+L)/2)- ((H-L)+(0.618*(H-L)))-(H-L)
print("srt1: ",srt1)

srt2= ((H+L)/2) - ((H-L)+(0.618*(H-L)))
print("srt2: ",srt2)

srsl=  ((H+L)/2)- ((H-L)+(0.618*(H-L))) -  ((H-L)+(0.618*(H-L))) - 3
print("srsl: ",srsl)

brtsl=(((H+L)/2)+(H-L)+(0.618*(H-L))) + ((H-L)+(0.618*(H-L)))
print("brtsl: ",brtsl)

srtsl = ((H+L)/2)- ((H-L)+(0.618*(H-L))) -  ((H-L)+(0.618*(H-L)))
print("srtsl: ",srtsl)