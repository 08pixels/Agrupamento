nota1 = int(input())
nota2 = int(input())
nota3 = int(input())
media = (nota1 + nota2 + nota3) / 3
if (media >= 7):
    print('Aprovado')
if (media < 3):
    print('Reprovado')
if (3 <=media<7):
    print('Prova final')
print('Sua nota foi', media,)

