player1 = input()
player2 = input()
print(player1,player2)
if player1 == player2:
    print('ничья')
elif player1 == 'бумага':
    if player2 == 'камень':
        print('win player1')
    else:
        print('win player2')