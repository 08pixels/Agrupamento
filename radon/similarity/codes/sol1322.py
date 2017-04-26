media1 = float(input())
media2= float(input())
media3= float(input())

media= (media1+media2+media3)/3

if(media >=7):
    print("aprovado")

elif(media < 3):
    print("reprovado")

elif(media>=3) and (media<7):
    print("prova final")
