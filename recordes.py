import json
import os

ARQUIVO = 'recordes.json'

def carregar():
    if not os.path.exists(ARQUIVO):
        return{}
    
    try:
        with open(ARQUIVO,'r') as f:
           return json.load(f)
    except (json.JSONDecodeError, IOError):
        return{}
    
def salvar(recordes):

    try:
        with open(ARQUIVO, 'w') as f:
            json.dump(recordes, f, indent=2)
    except IOError as e:
        print(f'[AVISO] Não foi possível salvar recordes: {e}')

def verificar_e_salvar(recordes, nome_pista, tempo_ms):
    recorde_atual = recordes.get(nome_pista, None)

    if recorde_atual is None or tempo_ms < recorde_atual:
        recordes[nome_pista] = tempo_ms
        salvar(recordes)
        return True
    
    return False