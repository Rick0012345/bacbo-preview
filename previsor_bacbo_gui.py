import tkinter as tk
from collections import defaultdict, Counter
import pandas as pd

# Fun es de previs o
def matriz_ordem_1(seq):
    trans = defaultdict(Counter)
    for a, b in zip(seq, seq[1:]):
        trans[a][b] += 1
    df = pd.DataFrame(trans).fillna(0).astype(int)
    prob = df.div(df.sum(axis=0), axis=1).round(2)
    return prob

def matriz_ordem_2(seq):
    trans = defaultdict(Counter)
    for a, b, c in zip(seq, seq[1:], seq[2:]):
        trans[(a, b)][c] += 1
    df = pd.DataFrame(trans).T.fillna(0).astype(int)
    prob = df.div(df.sum(axis=1), axis=0).round(2)
    return prob

def prever_por_blocos(seq, bloco_tam=3):
    blocos = defaultdict(list)
    for i in range(len(seq) - bloco_tam):
        chave = tuple(seq[i:i + bloco_tam])
        prox = seq[i + bloco_tam]
        blocos[chave].append(prox)
    ultimo_bloco = tuple(seq[-bloco_tam:])
    if ultimo_bloco in blocos:
        contagem = Counter(blocos[ultimo_bloco])
        total = sum(contagem.values())
        return {k: round(v / total, 2) for k, v in contagem.items()}
    return {}

def previsao_final(seq):
    if len(seq) < 4:
        return pd.Series()
    ordem1 = matriz_ordem_1(seq)
    ordem2 = matriz_ordem_2(seq)
    bloco_pred = prever_por_blocos(seq, 3)
    ultimo1 = seq[-1]
    ultimo2 = tuple(seq[-2:])
    pred_1 = ordem1[ultimo1] if ultimo1 in ordem1.columns else pd.Series()
    pred_2 = ordem2.loc[ultimo2] if ultimo2 in ordem2.index else pd.Series()
    pred_3 = pd.Series(bloco_pred)
    combined = (pred_1 * 0.2).add(pred_2 * 0.4, fill_value=0).add(pred_3 * 0.4, fill_value=0)
    return combined.sort_values(ascending=False).round(2)

# Interface Tkinter
class BacboApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Previsor Bac Bo")
        self.sequence = []
        self.total_correct = 0
        self.correct_high_conf = 0
        self.high_prob_count = 0
        self.last_prediction = None
        self.last_prob = None

        # Label da sequ ncia
        self.label_seq = tk.Label(master, text="Sequ ncia atual: []")
        self.label_seq.pack()

        # Estat sticas: rodadas, acertos e contadores
        self.stats_label = tk.Label(
            master,
            text="Rodadas: 0 | Acertos: 0 | Acertos >80%: 0 | Prob>75%: 0"
        )
        self.stats_label.pack(pady=5)

        # Bot es de input
        self.btn_frame = tk.Frame(master)
        self.btn_frame.pack()
        for text in ["B", "P", "T"]:
            btn = tk.Button(
                self.btn_frame,
                text=text,
                width=10,
                command=lambda t=text: self.adicionar_resultado(t)
            )
            btn.pack(side=tk.LEFT, padx=5, pady=5)

        # Label de resultado da previs o
        self.resultado_label = tk.Label(
            master,
            text="Previs o aparecer  aqui",
            font=("Arial", 12),
            justify=tk.LEFT,
            width=40,
            height=4,
            bg="SystemButtonFace"
        )
        self.resultado_label.pack(pady=10)

    def adicionar_resultado(self, resultado):
        # Atualiza sequ ncia e contagem de rodadas
        self.sequence.append(resultado)
        rodadas = len(self.sequence)
        self.label_seq.config(text=f"Sequ ncia atual: {' '.join(self.sequence)}")

        # Contagem de acertos s  ap s 20 rodadas
        if rodadas > 20 and self.last_prediction is not None:
            if resultado == self.last_prediction:
                self.total_correct += 1
                if self.last_prob and self.last_prob >= 0.8:
                    self.correct_high_conf += 1

        # Atualiza previs o para a pr xima rodada
        self.atualizar_previsao()

        # Conta probabilidades altas (>75%) somente ap s 20 rodadas
        if rodadas > 20 and self.last_prob is not None and self.last_prob > 0.75:
            self.high_prob_count += 1

        # Atualiza label de estat sticas
        self.stats_label.config(
            text=(
                f"Rodadas: {rodadas} | Acertos: {self.total_correct} | "
                f"Acertos >80%: {self.correct_high_conf} | Prob>75%: {self.high_prob_count}"
            )
        )

    def atualizar_previsao(self):
        resultado = previsao_final(self.sequence)
        if not resultado.empty:
            mais_provavel = resultado.idxmax()
            prob = resultado.max()
            self.last_prediction = mais_provavel
            self.last_prob = prob

            nome = {"B": "BANKER", "P": "PLAYER", "T": "TIE"}[mais_provavel]
            texto = f"Pr ximo resultado mais prov vel: {nome} ({int(prob * 100)}%)\n\n"
            texto += "Probabilidades completas:\n"
            for k, v in resultado.items():
                label = {"B": "Banker", "P": "Player", "T": "Tie"}[k]
                texto += f"- {label}: {int(v * 100)}%\n"

            # Ajuste de cor conforme confian a
            if prob < 0.3:
                self.resultado_label.config(bg="red")
            elif prob > 0.8:
                self.resultado_label.config(bg="green")
            else:
                self.resultado_label.config(bg="SystemButtonFace")
        else:
            texto = "Ainda n o h  dados suficientes para prever."
            self.last_prediction = None
            self.last_prob = None
            self.resultado_label.config(bg="SystemButtonFace")
        self.resultado_label.config(text=texto)

