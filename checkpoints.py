import math


class GerenciadorVoltas:

    def __init__(self, pista):
        self.pista         = pista
        self.volta_atual   = 0
        self.total_voltas  = pista["voltas"]
        self.checkpoints   = []
        self.cp_atingidos  = []
        self.ultima_detec  = 0    
        self.corrida_fim   = False

        self._construir_checkpoints()

    def _construir_checkpoints(self):

        pts = self.pista["pontos"]
        todos = list(pts) + [pts[0]]  

        self.checkpoints = []
        for i in range(len(todos) - 1):
            ax, ay = todos[i]
            bx, by = todos[i + 1]

     
            mx = (ax + bx) / 2
            my = (ay + by) / 2

            raio = self.pista["largura"] + 15

            self.checkpoints.append({
                "x": mx,
                "y": my,
                "raio": raio
            })

        # Todos começam como "não atingidos"
        self.cp_atingidos = [False] * len(self.checkpoints)



    def atualizar(self, carro_x, carro_y, tempo_atual_ms):
   
        if self.corrida_fim:
            return False

        volta_completa = False

        
        for i, cp in enumerate(self.checkpoints):
            if self.cp_atingidos[i]:
                continue  

            dist = math.hypot(carro_x - cp["x"], carro_y - cp["y"])
            if dist < cp["raio"]:
                self.cp_atingidos[i] = True

   
   
        qtd_atingidos    = sum(self.cp_atingidos)
        minimo_necessario = int(len(self.checkpoints) * 0.80)

        if (self.cp_atingidos[0]
                and qtd_atingidos >= minimo_necessario
                and tempo_atual_ms - self.ultima_detec > 2000):

            self.volta_atual  += 1
            self.ultima_detec  = tempo_atual_ms
            volta_completa     = True


            self.cp_atingidos = [False] * len(self.checkpoints)


            if self.volta_atual >= self.total_voltas:
                self.corrida_fim = True

        return volta_completa

  

    def resetar(self):

        self.volta_atual  = 0
        self.corrida_fim  = False
        self.ultima_detec = 0
        self.cp_atingidos = [False] * len(self.checkpoints)



    @property
    def progresso_texto(self):

        volta_exibida = min(self.volta_atual + 1, self.total_voltas)
        return f"VOLTA {volta_exibida} / {self.total_voltas}"

    @property
    def porcentagem_checkpoints(self):

        if not self.checkpoints:
            return 0.0
        return sum(self.cp_atingidos) / len(self.checkpoints)