import random

class Oceano:
    navio_por_quadrados = {'porta-aviões': 5, 'navio-tanque': 4, 'destroyer': 3, 'submarino': 3, 'navio-patrulha': 2}
    comprimento = 10

    def __init__(self, cor, tipo, name="Oceano"):
        self.name = name
        self.cor = cor
        self.tipo = tipo

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
        self.navio_por_status  = {navio: 'Em Combate' for navio in self.navio_por_quadrados}  # Todos começam em combate
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
                    # Verifique se a nova posição está dentro dos limites e se não colide com outros navios
                    if (0 <= int(proxima_posicao[1]) < self.comprimento and 
                        proxima_posicao_formatada in self.oceano_flat() and 
                        proxima_posicao_formatada not in navio_posicoes and 
                        proxima_posicao_formatada not in [pos for navio in posicao_navios.values() for pos in navio]):
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
        if self.tipo == "IA": print("OCEANO DO JOGADOR - IA ataca aqui. =====================")
        else: print("OCEANO DA IA - JOGADOR ataca aqui. =====================")

        for linha in self.oceano:
            linha_formatada = " ".join(f"| {self.colorir_item(item)} " for item in linha)
            linha_formatada += "|"
            print(linha_formatada)


    def atualizar_oceano(self, disparo):
        if disparo not in self.posicoes_tentadas:
            self.tentativas += 1  # O mesmo disparo não conta nova tentativa, só disparos diferentes
            if disparo not in self.oceano_flat():
                self.mostrar_oceano()
                print(f"\nHic sunt dracones! A célula {disparo} não está nos mares do mundo conhecido.\n")
                return True
            elif disparo not in self.lista_posicao_navios:
                self.posicoes_tentadas.append(disparo)
                self.mostrar_oceano()
                print(f"\nSPLASH! {self.name} mirou em {disparo} e acertou o mar.\n")
                return True
            else:
                self.navios_acertados.append(disparo)
                self.posicoes_tentadas.append(disparo)

                # Remove gerar_vizinhos from Oceano class; now handled by MarineIA
                
                self.mostrar_oceano()
                self.atualizar_status_navios()
                print(f"\nBOOM! {self.name} mirou em {disparo} e acertou um navio!\n")
        else:
            self.mostrar_oceano()
            print(f"\nVocê já tentou a posição {disparo} antes! Tente outra.\n")
            return True
        
    def atualizar_status_navios(self):
        # Verificar se o navio afundou com o disparo
        for tipo_navio, posicoes_navio in self.posicao_navios.items():
            if self.navio_por_status[tipo_navio] == 'Em Combate' and all(pos in self.navios_acertados for pos in posicoes_navio):
                print(f'\n{self.name} acaba de afundar um {tipo_navio}!')
                self.navio_por_status[tipo_navio] = 'Naufragado'

        # Verificar se todos os navios foram afundados                    
        if all(item in self.navios_acertados for item in self.lista_posicao_navios):
            print(f"\n{self.name} afundou todos os navios do adversário. O jogo deverá se encerrar agora!")
            print(f"Total de tentativas: {self.tentativas}")
            exit()
            return False
        else:
           # print(self.navio_por_status)
            return True
    

class MarineIA:
    def __init__(self, sequencias_possiveis_posicoes):
        self.sequencias_possiveis_posicoes = sequencias_possiveis_posicoes
        self.lista_coordenadas_usadas = []
        self.lista_acertos = []
        self.lista_erros = []
        self.coordenadas_vizinhancas = []
        self.orientacao = None
        self.ultimo_disparo_afundou = False  # Nova variável para controlar o estado do último disparo

    def atirar(self):
        # Se o último disparo afundou um navio, atirar aleatoriamente
        if self.ultimo_disparo_afundou:
            while True:
                coordenadas = random.choice(list(set(self.sequencias_possiveis_posicoes) - set(self.lista_coordenadas_usadas)))
                return coordenadas

        # Priorizar as coordenadas vizinhas se existirem
        if self.coordenadas_vizinhancas:
            for coord in self.coordenadas_vizinhancas:
                if coord not in self.lista_coordenadas_usadas:
                    self.coordenadas_vizinhancas.remove(coord)  # Remove used neighbors
                    return coord  # Shoot at the first available neighbor

        # Se não houver vizinhos, atirar aleatoriamente
        while True:
            coordenadas = random.choice(list(set(self.sequencias_possiveis_posicoes) - set(self.lista_coordenadas_usadas)))
            return coordenadas

    def atualizar_memoria_maquina(self, informacao, coordenadas):
        self.lista_coordenadas_usadas.append(coordenadas)

        if coordenadas in self.sequencias_possiveis_posicoes:
            self.sequencias_possiveis_posicoes.remove(coordenadas)

        if informacao == 1:  # Acerto
            self.lista_acertos.append(coordenadas)
            # Deduzir a orientação após acertos consecutivos
            self.deduzir_orientacao()

            # Gerar vizinhos e adicionar à lista de coordenadas vizinhas
            vizinhos = self.gerar_vizinhos(coordenadas)
            self.coordenadas_vizinhancas.extend([v for v in vizinhos if v not in self.lista_coordenadas_usadas])

            # Verificar se o último disparo afundou um navio
            self.ultimo_disparo_afundou = self.verificar_ultimo_disparo_afundou()

        elif informacao == 2:  # Erro
            self.lista_erros.append(coordenadas)
            self.orientacao = None  # Resetar orientação ao errar
            self.ultimo_disparo_afundou = False  # Resetar a variável

    def gerar_vizinhos(self, coordenadas):
        vizinhos = []
        letra, numero = coordenadas[0], int(coordenadas[1:])

        if self.orientacao == 'horizontal':
            candidatos = [
                f"{chr(ord(letra) - 1)}{numero}",  # Esquerda
                f"{chr(ord(letra) + 1)}{numero}"   # Direita
            ]
        elif self.orientacao == 'vertical':
            candidatos = [
                f"{letra}{numero - 1}",  # Cima
                f"{letra}{numero + 1}"   # Baixo
            ]
        else:
            # Caso não haja orientação definida, adivinhar em cruz
            candidatos = [
                f"{chr(ord(letra) - 1)}{numero}",
                f"{chr(ord(letra) + 1)}{numero}",
                f"{letra}{numero - 1}",
                f"{letra}{numero + 1}"
            ]

        for candidato in candidatos:
            if candidato in self.sequencias_possiveis_posicoes and candidato not in self.lista_coordenadas_usadas:
                vizinhos.append(candidato)

        print('orientacao', self.orientacao)
        print('candidatos', candidatos)
        print('vizinhos', vizinhos)

        return vizinhos

    def deduzir_orientacao(self):
        if len(self.lista_acertos) > 1:
            # Verifica a orientação com base nos últimos dois acertos
            if (self.lista_acertos[-1][0] == self.lista_acertos[-2][0] and 
                abs(int(self.lista_acertos[-1][1:]) - int(self.lista_acertos[-2][1:])) == 1):
                self.orientacao = 'vertical'
                self.coordenadas_vizinhancas.extend([f"{self.lista_acertos[-1][0]}{int(self.lista_acertos[-1][1:]) + 1}",
                                                      f"{self.lista_acertos[-1][0]}{int(self.lista_acertos[-1][1:]) - 1}"])
            elif (self.lista_acertos[-1][1:] == self.lista_acertos[-2][1:] and 
                  abs(ord(self.lista_acertos[-1][0]) - ord(self.lista_acertos[-2][0])) == 1):
                self.orientacao = 'horizontal'
                self.coordenadas_vizinhancas.extend([f"{chr(ord(self.lista_acertos[-1][0]) + 1)}{self.lista_acertos[-1][1:]}",
                                                      f"{chr(ord(self.lista_acertos[-1][0]) - 1)}{self.lista_acertos[-1][1:]}"])

    def verificar_ultimo_disparo_afundou(self):
        if not self.lista_acertos:
            return False
        for tipo_navio, posicoes_navio in atlantico.posicao_navios.items():
            if atlantico.navio_por_status[tipo_navio] == 'Em Combate' and all(pos in self.lista_acertos for pos in posicoes_navio):
                atlantico.navio_por_status[tipo_navio] = 'Naufragado'
                print(f'\n"IA acaba de afundar um {tipo_navio}!')
                self.orientacao = None  # Resetar orientação após afundar
                self.coordenadas_vizinhancas.clear()  # Resetar vizinhos após afundar
                return True
        return False

    def tamanho_maior_navio_restante(self):
        navios_restantes = [tipo_navio for tipo_navio in atlantico.posicao_navios.keys() if atlantico.navio_por_status[tipo_navio] == 'Em Combate']
        if not navios_restantes:
            return 0
        return max(len(atlantico.posicao_navios[tipo_navio]) for tipo_navio in navios_restantes)

def main():
    rodar = True
    turno = 0

    print("\n////// SUPA NAVAL BATTLE v0.1 //////\n")
    modo_jogo = input("Escolha o modo de jogo:\n1 - Apenas IA\n2 - Apenas Usuário\n3 - Usuário contra Máquina\nDigite sua opção: ")
    
    # Instancia a IA com a lista de posições possíveis
    ia = MarineIA(atlantico.sequencias_possiveis_posicoes())

    # IA SOZINHA
    if modo_jogo == "1":
        print("\n----------------------------------------------------------------\n")
        while rodar:
            ia_disparo = ia.atirar()
            
            if ia_disparo not in atlantico.lista_posicao_navios:
                ia.atualizar_memoria_maquina(2, ia_disparo)
            if ia_disparo in atlantico.lista_posicao_navios:
                ia.atualizar_memoria_maquina(1, ia_disparo)
            if atlantico.atualizar_oceano(ia_disparo) == False:
                break
            
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
            turno += 1
            ia_disparo = ia.atirar()
            
            if ia_disparo not in atlantico.lista_posicao_navios: ia.atualizar_memoria_maquina(2, ia_disparo)
            if ia_disparo in atlantico.lista_posicao_navios: ia.atualizar_memoria_maquina(1, ia_disparo)
            if atlantico.atualizar_oceano(ia_disparo) == False: break
            if turno == 1: pacifico.mostrar_oceano()
            elif pacifico.atualizar_oceano(disparo.upper()) == False: break
                
            disparo = input("Digite qual célula deseja atacar (ou 0 para encerrar): ")
            
            if disparo == '0':
                break

if __name__ == "__main__":
    atlantico = Oceano(name="Atlântico", tipo="IA", cor=True)
    pacifico = Oceano(name="Pacífico", tipo="Jogador", cor=False)
    main()