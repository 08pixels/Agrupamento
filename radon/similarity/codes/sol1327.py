
nota1 = float(input("Digite sua primeira nota: "))
nota2 = float(input("Digite sua segunda nota: "))
nota3 = float(input("Digite sua terceira nota: "))
media = (nota1 + nota2 + nota3)/3
print(media)
if media >= 7:
    print("aprovado")
elif media <3:
    print("reprovado")
elif 3<=media<7:
    print("prova final")
    
