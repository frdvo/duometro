import csv
from collections import defaultdict

# Configuração - altere estes valores
ARQUIVO_ANTIGO = 'restaurantes_com_metro_google_anterior.csv'
ARQUIVO_NOVO = 'restaurantes_com_metro_google.csv'

# Emojis para decorar a saída
EMOJI_REMOVIDO = "❌"
EMOJI_ADICIONADO = "🆕"
EMOJI_MODIFICADO = "🔄"
EMOJI_METRO = "🚇"
EMOJI_DISTANCIA = "📏"
EMOJI_TEMPO = "⏱️"

# Campos de dias da semana para formatação especial
CAMPOS_ALMOCO = ['almoco_dom', 'almoco_seg', 'almoco_ter', 'almoco_qua', 'almoco_qui', 'almoco_sex', 'almoco_sab']
CAMPOS_JANTAR = ['jantar_dom', 'jantar_seg', 'jantar_ter', 'jantar_qua', 'jantar_qui', 'jantar_sex', 'jantar_sab']
DIAS_SEMANA = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sab']

# Campos relacionados a metrô para tratamento especial
CAMPOS_METRO = ['Estacao', 'Distancia', 'Tempo']

def ler_restaurantes(arquivo):
    restaurantes = {}
    with open(arquivo, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nome = row['nome']
            dados = {k.strip(): v.strip() if isinstance(v, str) else v for k, v in row.items()}
            restaurantes[nome] = dados
    return restaurantes

def formatar_horarios(dados):
    almoco = []
    jantar = []
    
    for dia in DIAS_SEMANA:
        almoco.append('X' if dados.get(f'almoco_{dia.lower()}') == 'X' else ' ')
        jantar.append('X' if dados.get(f'jantar_{dia.lower()}') == 'X' else ' ')
    
    cabecalho = ' ' * 14 + ' '.join(f'{dia:>3}' for dia in DIAS_SEMANA)
    linha_almoco = 'Almoço      ' + ' '.join(f'{x:>3}' for x in almoco)
    linha_jantar = 'Jantar      ' + ' '.join(f'{x:>3}' for x in jantar)
    
    return f"{cabecalho}\n{linha_almoco}\n{linha_jantar}"

def formatar_campo_metro(campo, valor):
    if campo == 'Estacao':
        return f"{EMOJI_METRO} Estação: {valor}"
    elif campo == 'Distancia':
        return f"{EMOJI_DISTANCIA} Distância: {valor}m"
    elif campo == 'Tempo':
        return f"{EMOJI_TEMPO} Tempo a pé: {valor}min"
    return f"{campo}: {valor}"

def comparar_restaurantes(antigos, novos):
    removidos = set(antigos.keys()) - set(novos.keys())
    adicionados = set(novos.keys()) - set(antigos.keys())
    modificados = defaultdict(dict)
    
    for nome in set(antigos.keys()) & set(novos.keys()):
        antigo = antigos[nome]
        novo = novos[nome]
        campos_modificados = {}
        
        for campo in set(antigo.keys()).union(set(novo.keys())):
            valor_antigo = antigo.get(campo, '')
            valor_novo = novo.get(campo, '')
            
            if valor_antigo != valor_novo:
                campos_modificados[campo] = {'antigo': valor_antigo, 'novo': valor_novo}
        
        if campos_modificados:
            modificados[nome] = campos_modificados
    
    return removidos, adicionados, modificados

def main():
    print(f"🔍 Comparando arquivos: {ARQUIVO_ANTIGO} (antigo) e {ARQUIVO_NOVO} (novo)")
    
    try:
        antigos = ler_restaurantes(ARQUIVO_ANTIGO)
        novos = ler_restaurantes(ARQUIVO_NOVO)
        removidos, adicionados, modificados = comparar_restaurantes(antigos, novos)
        
        # Restaurantes removidos
        print(f"\n{EMOJI_REMOVIDO} {len(removidos)} Restaurantes removidos do Duo Gourmet:")
        for nome in sorted(removidos):
            print(f"  - {nome}")
        
        # Restaurantes adicionados
        print(f"\n{EMOJI_ADICIONADO} {len(adicionados)} Restaurantes adicionados ao Duo Gourmet:")
        for nome in sorted(adicionados):
            print(f"  - {nome}")
        
        # Restaurantes modificados
        print(f"\n{EMOJI_MODIFICADO} {len(modificados)} Restaurantes modificados:")
        for nome, campos in sorted(modificados.items()):
            print(f"\n{EMOJI_MODIFICADO} {nome}:")
            
            # Verificar se há mudanças nos horários
            tem_horarios_modificados = any(campo in CAMPOS_ALMOCO + CAMPOS_JANTAR for campo in campos.keys())
            tem_metro_modificado = any(campo in CAMPOS_METRO for campo in campos.keys())
            
            # Mostrar horários se modificados
            if tem_horarios_modificados:
                print("\n  🕒 Horários Antigos:")
                print(f"  {formatar_horarios(antigos[nome])}")
                print("\n  🕒 Horários Novos:")
                print(f"  {formatar_horarios(novos[nome])}")
            
            # Mostrar informações de metrô se modificadas
            if tem_metro_modificado:
                print("\n  🚇 Informações de Metrô Modificadas:")
                for campo in CAMPOS_METRO:
                    if campo in campos:
                        print(f"  - Antigo: {formatar_campo_metro(campo, campos[campo]['antigo'])}")
                        print(f"  - Novo:   {formatar_campo_metro(campo, campos[campo]['novo'])}")
            
            # Mostrar outros campos modificados
            outros_campos = {k: v for k, v in campos.items() 
                           if k not in CAMPOS_ALMOCO + CAMPOS_JANTAR + CAMPOS_METRO}
            
            if outros_campos:
                print("\n  📝 Outras modificações:")
                for campo, valores in outros_campos.items():
                    print(f"  - Campo '{campo}':")
                    print(f"      Antigo: {valores['antigo']}")
                    print(f"      Novo:   {valores['novo']}")
    
    except FileNotFoundError as e:
        print(f"❌ Erro: Arquivo não encontrado - {e.filename}")
    except Exception as e:
        print(f"⚠️ Ocorreu um erro: {str(e)}")

if __name__ == "__main__":
    main()