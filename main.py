import random

class Oceano:
    navio_por_quadrados = {'porta_avioes': 5, 'navio_tanque': 4, 'destroier': 3, 'submarino': 2}
    navios_por_status = {navio: 'Em Combate' for navio in navio_por_quadrados}  # Todos começam em combate
    comprimento = 10

    def __init__(self, cor, name="Oceano"):
        self.name = name
        self.cor = cor

        matriz = []
        for i in range(self.comprimento):
            linha = []
            for j in range(self.comprimento):
                letra = chr(65 + j)
                linha.append(f"{letra}{i}")
            matriz.append(linha)
        self.oceano = matriz

        # Adiciona os navios na matriz
        self.posicao_navios = self.colocar_navios()
        self.lista_posicao_navios = [pos for navio in self.posicao_navios.values() for pos in navio]

        self.verde = "\033[92m" if self.cor else ""
        self.vermelho = "\033[91m"
        self.azul = "\033[34m"
        self.reset = "\033[0m"
        self.navios_acertados = []
        self.posicoes_tentadas = []
        self.tentativas = 0

    def colocar_navios(self):
        posicao_navios = {}
        sequencias_possiveis = self.sequencias_possiveis_posicoes()
        for tipo_navio, tamanho in self.navio_por_quadrados.items():
            colocado = False
            while not colocado:
                inicio = random.choice(sequencias_possiveis)
                direcao = random.choice([(0, 1), (1, 0)])  # Direção horizontal (0, 1) ou vertical (1, 0)
                navio_posicoes = [inicio]
                for _ in range(tamanho - 1):
                    ultima_posicao = navio_posicoes[-1]
                    proxima_posicao = (
                        chr(ord(ultima_posicao[0]) + direcao[0]),
                        int(ultima_posicao[1:]) + direcao[1]
                    )
                    proxima_posicao_formatada = f"{proxima_posicao[0]}{proxima_posicao[1]}"
                    if proxima_posicao_formatada in self.oceano_flat() and proxima_posicao_formatada not in navio_posicoes:
                        navio_posicoes.append(proxima_posicao_formatada)
                    else:
                        break
                if len(navio_posicoes) == tamanho:
                    posicao_navios[tipo_navio] = navio_posicoes
                    colocado = True
                    # Remove as posições usadas para evitar colisões de navios
                    sequencias_possiveis = [pos for pos in sequencias_possiveis if pos not in navio_posicoes]
        return posicao_navios

    def sequencias_possiveis_posicoes(self):
        sequencias = []
        for linha in self.oceano:
            sequencias.extend(linha)
        return sequencias

    def oceano_flat(self):
        return [item for sublist in self.oceano for item in sublist]

    def colorir_item(self, item):
        if item in self.navios_acertados:
            return f"{self.vermelho}{item}{self.reset}"
        
        elif item in self.posicoes_tentadas:
            return f"{self.azul}{item}{self.reset}"
        
        elif item in self.lista_posicao_navios:
            return f"{self.verde}{item}{self.reset}" if self.cor else item
        return item

    def mostrar_oceano(self):
        for linha in self.oceano:
            linha_formatada = " ".join(f"| {self.colorir_item(item)} " for item in linha)
            linha_formatada += "|"
            print(linha_formatada)

    def atualizar_oceano(self, disparo):
        if disparo not in self.posicoes_tentadas:
            self.tentativas += 1  # O mesmo disparo não conta nova tentativa, só disparos diferentes
            if disparo not in self.oceano_flat():
                print(f"Hic sunt dracones! Essa célula não está nos mares do mundo conhecido.\n")
                return True
            elif disparo not in self.lista_posicao_navios:
                print(f"SPLASH! {self.name} acertou o mar.\n")
                self.posicoes_tentadas.append(disparo)
                return True
            else:
                print(f"BOOM! {self.name} acertou um navio!\n")
                self.navios_acertados.append(disparo)
                self.posicoes_tentadas.append(disparo)

                vizinhos = self.gerar_vizinhos(disparo)
                # print(f"Coordenadas vizinhas de {disparo}: {vizinhos}")      
                          
                self.atualizar_status_navios()
        else:
            print(f"Você já tentou a posição {disparo} antes! Tente outra.")
            return True

    def atualizar_status_navios(self):
        # Verificar se o navio afundou com o disparo
        for tipo_navio, posicoes_navio in self.posicao_navios.items():
            if self.navios_por_status[tipo_navio] == 'Em Combate' and all(pos in self.navios_acertados for pos in posicoes_navio):
                print(f'{self.name} acaba de afundar um {tipo_navio}!\n')
                self.navios_por_status[tipo_navio] = 'Naufragado'

        # Verificar se todos os navios foram afundados                    
        if all(item in self.navios_acertados for item in self.lista_posicao_navios):
            print("Você afundou todos os navios. O jogo deverá se encerrar agora!")
            print(f"Total de tentativas: {self.tentativas}")
            return False
        else:
            return True
    

    def gerar_vizinhos(self, coordenadas):
        vizinhos = []
        letra, numero = coordenadas[0], int(coordenadas[1:])
        candidatos = [
            f"{chr(ord(letra) - 1)}{numero}",  # Esquerda
            f"{chr(ord(letra) + 1)}{numero}",  # Direita
            f"{letra}{numero - 1}",            # Cima
            f"{letra}{numero + 1}"             # Baixo
        ]
        for candidato in candidatos:
            if candidato in self.oceano_flat():
                vizinhos.append(candidato)
        return vizinhos


class MarineIA:
    def __init__(self, sequencias_possiveis_posicoes):
        self.sequencias_possiveis_posicoes = sequencias_possiveis_posicoes
        self.lista_coordenadas_usadas = []
        self.lista_acertos = []
        self.lista_erros = []
        self.coordenadas_vizinhancas = []
    
    def atirar(self):
        # Priorizar as coordenadas vizinhas se existirem
        if self.coordenadas_vizinhancas:
            coordenadas = self.coordenadas_vizinhancas.pop(0)  # Remover e tentar o primeiro vizinho
            return coordenadas
        
        # Se não houver vizinhos, atirar aleatoriamente
        while True:
            coordenadas = random.choice(self.sequencias_possiveis_posicoes)
            if coordenadas not in self.lista_coordenadas_usadas:
                return coordenadas

    def atualizar_memoria_maquina(self, informacao, coordenadas):
        self.lista_coordenadas_usadas.append(coordenadas)
        # Remove a coordenada da lista de possíveis posições
        if coordenadas in self.sequencias_possiveis_posicoes:
            self.sequencias_possiveis_posicoes.remove(coordenadas)
        
        if informacao == 1:  # Acerto
            self.lista_acertos.append(coordenadas)
            # Gerar vizinhos e adicionar à lista de coordenadas vizinhas
            vizinhos = self.gerar_vizinhos(coordenadas)
            self.coordenadas_vizinhancas.extend([v for v in vizinhos if v not in self.lista_coordenadas_usadas])
        elif informacao == 2:  # Erro
            self.lista_erros.append(coordenadas)

    def gerar_vizinhos(self, coordenadas):
        vizinhos = []
        letra, numero = coordenadas[0], int(coordenadas[1:])
        candidatos = [
            f"{chr(ord(letra) - 1)}{numero}",  # Esquerda
            f"{chr(ord(letra) + 1)}{numero}",  # Direita
            f"{letra}{numero - 1}",            # Cima
            f"{letra}{numero + 1}"             # Baixo
        ]
        for candidato in candidatos:
            if candidato in self.sequencias_possiveis_posicoes:
                vizinhos.append(candidato)
        return vizinhos


# Instancia um oceano
atlantico = Oceano(name="Atlântico", cor=True)
pacifico = Oceano(name="Pacífico", cor=False)

# Instancia a IA com a lista de posições possíveis
ia = MarineIA(atlantico.sequencias_possiveis_posicoes())

rodar = True

print("\n////// SUPA NAVAL BATTLE v0.1 //////\n")
modo_jogo = input("Escolha o modo de jogo:\n1 - Apenas IA\n2 - Apenas Usuário\n3 - Usuário contra Máquina\nDigite sua opção: ")

# IA SOZINHA
if modo_jogo == "1":
    print("\n----------------------------------------------------------------\n")
    while rodar:
        atlantico.mostrar_oceano()

        ia_disparo = ia.atirar()
        print(f"\nIA atirou em: {ia_disparo}\n")
        rodar = atlantico.atualizar_oceano(ia_disparo)
        if ia_disparo not in atlantico.lista_posicao_navios:
            ia.atualizar_memoria_maquina(2, ia_disparo)
        if ia_disparo in atlantico.lista_posicao_navios:
            ia.atualizar_memoria_maquina(1, ia_disparo)
        
        continuar = input("Digite 1 para a IA tentar outro disparo ou 0 para encerrar o jogo: ")
        if continuar == "0":
            break

# JOGADOR SOZINHO
elif modo_jogo == "2":
    print("\n----------------------------------------------------------------\n")
    while rodar:
        atlantico.mostrar_oceano()
        disparo = input("Digite qual célula deseja atacar (ou 0 para encerrar): ")
        rodar = atlantico.atualizar_oceano(disparo.upper())

# JOGADOR VS IA
elif modo_jogo == "3":
        print("\n----------------------------------------------------------------\n")
        while rodar:
            print("OCEANO DO JOGADOR - IA ataca aqui. =====================")
            atlantico.mostrar_oceano() # Printa matriz todo novo chute de IA
            print("\n")
            print("OCEANO DA IA - Jogador ataca aqui =====================")
            pacifico.mostrar_oceano() # Printa a matriz todo novo chute de Jogador
            ia_disparo = ia.atirar()
            print(f"\nIA atirou em: {ia_disparo}\n")
            
            if ia_disparo not in atlantico.lista_posicao_navios:
                ia.atualizar_memoria_maquina(2, ia_disparo)
            if ia_disparo in atlantico.lista_posicao_navios:
                ia.atualizar_memoria_maquina(1, ia_disparo)
            disparo = input("Digite qual célula deseja atacar (ou 0 para encerrar): ")
            print(f"Jogador atirou em: {disparo}\n")


            if (pacifico.atualizar_oceano(disparo.upper()) == False or
            atlantico.atualizar_oceano(ia_disparo)) == False:
                break

            if disparo == 0:
                break