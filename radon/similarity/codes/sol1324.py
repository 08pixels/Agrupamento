n1=float(input())
n2=float(input())
n3=float(input())
media=(n1+n2+n3)/3
if media>=7:
    x="aprovado"
elif 3<=media<7:
    x="prova final"
else:
    x="reprovado"
print(x)
