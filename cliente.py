import socket
import threading
import tkinter as tk
from tkinter import simpledialog, messagebox

HOST = '172.16.15.254'  # IP do servidor
PORT = 5000         # Porta do servidor

class ClienteBatalhaNaval:
    def __init__(self, master):
        self.master = master
        self.master.title("Batalha Naval")
        self.meu_nome = ""
        self.nome_adversario = ""
        self.seu_turno = False
        self.tabuleiro = [[0]*7 for _ in range(7)]  # 0=água, 1=navio, 2=acertado, 3=erro
        self.tabuleiro_oponente = [[0]*7 for _ in range(7)]
        self.botoes_meu = []
        self.botoes_oponente = []

        self.conexao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conexao.connect((HOST, PORT))

        self.tela_inicio()

        threading.Thread(target=self.escutar_servidor, daemon=True).start()

    def tela_inicio(self):
        self.frame_inicio = tk.Frame(self.master)
        self.frame_inicio.pack(pady=20)

        tk.Label(self.frame_inicio, text="Seu nome:").pack()
        self.nome_entry = tk.Entry(self.frame_inicio)
        self.nome_entry.pack()

        tk.Button(self.frame_inicio, text="Criar Partida", command=self.criar_partida).pack(pady=5)
        tk.Button(self.frame_inicio, text="Entrar em Partida", command=self.entrar_partida).pack()

    def criar_partida(self):
        nome = self.nome_entry.get()
        if nome:
            self.meu_nome = nome
            self.conexao.send(f"{nome}|CRIAR".encode())

    def entrar_partida(self):
        nome = self.nome_entry.get()
        if nome:
            id_partida = simpledialog.askinteger("Entrar", "ID da Partida:")
            if id_partida:
                self.meu_nome = nome
                self.conexao.send(f"{nome}|ENTRAR|{id_partida}".encode())

    def iniciar_jogo(self):
        self.frame_inicio.destroy()
        self.frame_jogo = tk.Frame(self.master)
        self.frame_jogo.pack()

        tk.Label(self.frame_jogo, text="Seu Tabuleiro").grid(row=0, column=0, padx=20)
        tk.Label(self.frame_jogo, text="Tabuleiro do Oponente").grid(row=0, column=1, padx=20)

        frame_esquerda = tk.Frame(self.frame_jogo)
        frame_esquerda.grid(row=1, column=0)

        frame_direita = tk.Frame(self.frame_jogo)
        frame_direita.grid(row=1, column=1)

        for i in range(7):
            linha_esq = []
            linha_dir = []
            for j in range(7):
                btn_meu = tk.Button(frame_esquerda, width=3, height=1, bg="blue", state="disabled")
                btn_meu.grid(row=i, column=j)
                linha_esq.append(btn_meu)

                btn_opp = tk.Button(frame_direita, width=3, height=1, command=lambda x=i, y=j: self.atacar(x, y))
                btn_opp.grid(row=i, column=j)
                linha_dir.append(btn_opp)

            self.botoes_meu.append(linha_esq)
            self.botoes_oponente.append(linha_dir)

    def escutar_servidor(self):
        buffer = ""
        while True:
            try:
                dados = self.conexao.recv(2048).decode()
                if not dados:
                    break

                buffer += dados
                while '\n' in buffer:
                    linha, buffer = buffer.split('\n', 1)
                    self.processar_mensagem(linha.strip())

            except Exception as e:
                print("Erro na comunicação:", e)
                break

    def processar_mensagem(self, dados):
        if dados.startswith("PARTIDA_CRIADA"):
            id_partida = dados.split('|')[1]
            messagebox.showinfo("Partida Criada", f"ID da Partida: {id_partida}\nAguardando outro jogador...")

        elif dados.startswith("PARTIDA_INICIADA"):
            self.nome_adversario = dados.split('|')[1]
            self.iniciar_jogo()

        elif dados.startswith("TABULEIRO|"):
            tab_str = dados.split('|')[1]
            linhas = tab_str.split(';')
            for i in range(7):
                for j in range(7):
                    val = int(linhas[i].split(',')[j])
                    self.tabuleiro[i][j] = val
                    if val == 1:
                        self.botoes_meu[i][j].config(bg="gray")

        elif dados.startswith("SEU_TURNO"):
            self.seu_turno = dados.split('|')[1] == "True"
            status = "Seu turno!" if self.seu_turno else "Turno do oponente..."
            self.master.title(f"Batalha Naval - {status}")

        elif dados.startswith("RESULTADO"):
            _, resultado, x, y = dados.split('|')
            x, y = int(x), int(y)
            cor = "red" if resultado == "ACERTOU" else "white"
            self.botoes_oponente[x][y].config(bg=cor)

        elif dados.startswith("ATAQUE_ADVERSARIO"):
            _, resultado, x, y = dados.split('|')
            x, y = int(x), int(y)
            cor = "red" if resultado == "ACERTOU" else "white"
            self.botoes_meu[x][y].config(bg=cor)

        elif dados == "VITORIA":
            messagebox.showinfo("Fim de Jogo", "Você venceu!")
            self.master.quit()

        elif dados == "DERROTA":
            messagebox.showinfo("Fim de Jogo", "Você perdeu.")
            self.master.quit()

    def atacar(self, x, y):
        if not self.seu_turno:
            return
        self.conexao.send(f"ATAQUE|{x}|{y}".encode())
        self.seu_turno = False


if __name__ == "__main__":
    root = tk.Tk()
    app = ClienteBatalhaNaval(root)
    root.mainloop()
