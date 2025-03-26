from conexao import Conexao

# Pergunta o nome do jogador
nome_jogador = input("Digite seu nome: ").strip()

# Pergunta se este jogador quer criar ou entrar numa partida existente

print(f"1 - Criar partida\n2 - Entrar em uma partida existente\n3 - Sair")

# Lê a escolha do usuário e garante que seja um número válido
opcao = input("Escolha a opção: ").strip()

# Definir a variável 'servidor' com base na escolha do usuário
if opcao == '1':
    servidor = True  # Criar partida (servidor)
    ip = "localhost"  # O servidor fica em localhost
elif opcao == '2':
    servidor = False  # Entrar em uma partida existente (cliente)
    ip = input("Digite o IP do outro jogador: ")  # Pede o IP do adversário
elif opcao == '3':
    print("Saindo...")  # Mensagem de saída
    exit()  # Encerra o programa
else:
    print("Opção inválida!")
    exit()  # Encerra o programa caso a opção seja inválida


# Inicia a conexão
conexao = Conexao(servidor, nome_jogador, ip)

# Loop para enviar mensagens
while True:
    mensagem = input()
    conexao.enviar_mensagem(mensagem)
