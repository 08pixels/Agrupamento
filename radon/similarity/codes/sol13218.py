nun1=float(input())
nun2=float(input())
nun3=float(input())
media=(nun1+nun2+nun3)/3
if(media<=3):
    print("reprovado")
elif(media<7) and (media>3):
    print("prova final")
elif(media>=7):
    print("aprovado")
