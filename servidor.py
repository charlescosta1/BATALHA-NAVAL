import socket
import threading
import random

HOST = '0.0.0.0'
PORT = 5000

partidas = {}
lock = threading.Lock()

class Partida:
    def __init__(self, id_partida):
        self.id = id_partida
        self.jogadores = []
        self.tabuleiros = {}
        self.turno = 0  # 0 ou 1
        self.conexoes = {}

    def adicionar_jogador(self, nome, conn):
        self.jogadores.append(nome)
        self.conexoes[nome] = conn
        self.tabuleiros[nome] = self.gerar_tabuleiro()

    def gerar_tabuleiro(self):
        tabuleiro = [[0] * 7 for _ in range(7)]
        navios = 5
        while navios > 0:
            x = random.randint(0, 6)
            y = random.randint(0, 6)
            if tabuleiro[x][y] == 0:
                tabuleiro[x][y] = 1
                navios -= 1
        return tabuleiro

    def outro_jogador(self, nome):
        return self.jogadores[1] if self.jogadores[0] == nome else self.jogadores[0]

    def jogador_atual(self):
        return self.jogadores[self.turno]

    def alternar_turno(self):
        self.turno = 1 - self.turno


def tratar_cliente(conn, addr):
    print(f"[+] Nova conexão de {addr}")
    nome = ""
    partida = None

    try:
        msg = conn.recv(1024).decode()
        dados = msg.split('|')

        if dados[1] == "CRIAR":
            nome = dados[0]
            with lock:
                id_partida = len(partidas) + 1
                partida = Partida(id_partida)
                partida.adicionar_jogador(nome, conn)
                partidas[id_partida] = partida
            conn.send(f"PARTIDA_CRIADA|{id_partida}\n".encode())

        elif dados[1] == "ENTRAR":
            nome = dados[0]
            id_partida = int(dados[2])
            with lock:
                if id_partida not in partidas or len(partidas[id_partida].jogadores) >= 2:
                    conn.send("PARTIDA_NAO_ENCONTRADA\n".encode())
                    return

                partida = partidas[id_partida]
                partida.adicionar_jogador(nome, conn)

                # Inicia partida
                j1 = partida.jogadores[0]
                j2 = partida.jogadores[1]

                partida.conexoes[j1].send(f"PARTIDA_INICIADA|{j2}\n".encode())
                partida.conexoes[j2].send(f"PARTIDA_INICIADA|{j1}\n".encode())

                # Envia tabuleiros
                for jogador in partida.jogadores:
                    tab = partida.tabuleiros[jogador]
                    tab_str = ';'.join([','.join(map(str, linha)) for linha in tab])
                    partida.conexoes[jogador].send(f"TABULEIRO|{tab_str}\n".encode())

                # Inicia turnos
                partida.conexoes[j1].send("SEU_TURNO|True\n".encode())
                partida.conexoes[j2].send("SEU_TURNO|False\n".encode())

        while True:
            dados = conn.recv(1024).decode()
            if not dados:
                break

            if dados.startswith("ATAQUE"):
                _, x, y = dados.split('|')
                x, y = int(x), int(y)
                atual = nome
                adversario = partida.outro_jogador(atual)
                tabuleiro_adv = partida.tabuleiros[adversario]

                if tabuleiro_adv[x][y] == 1:
                    tabuleiro_adv[x][y] = 2
                    resultado = "ACERTOU"
                else:
                    tabuleiro_adv[x][y] = 3
                    resultado = "ERROU"

                # Resultado para atacante
                partida.conexoes[atual].send(f"RESULTADO|{resultado}|{x}|{y}\n".encode())

                # Informação para defensor
                partida.conexoes[adversario].send(f"ATAQUE_ADVERSARIO|{resultado}|{x}|{y}\n".encode())

                # Verifica fim de jogo
                navios_restantes = sum(row.count(1) for row in tabuleiro_adv)
                if navios_restantes == 0:
                    partida.conexoes[atual].send("VITORIA\n".encode())
                    partida.conexoes[adversario].send("DERROTA\n".encode())
                    break
                else:
                    partida.alternar_turno()
                    for jogador in partida.jogadores:
                        turno = "True" if jogador == partida.jogador_atual() else "False"
                        partida.conexoes[jogador].send(f"SEU_TURNO|{turno}\n".encode())

            elif dados == "TABULEIRO":
                tabuleiro = partida.tabuleiros[nome]
                tab_str = ';'.join([','.join(map(str, linha)) for linha in tabuleiro])
                conn.send(f"TABULEIRO|{tab_str}\n".encode())

    except Exception as e:
        print(f"Erro com cliente {addr}: {e}")

    finally:
        conn.close()
        print(f"[-] Conexão encerrada de {addr}")


def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen()
    print(f"[+] Servidor escutando em {HOST}:{PORT}")

    while True:
        conn, addr = servidor.accept()
        threading.Thread(target=tratar_cliente, args=(conn, addr), daemon=True).start()


if __name__ == "__main__":
    main()
