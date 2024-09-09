# Importando bibliotecas
from datetime import datetime
import pandas as pd
import csv
import os

# Obtendo o caminho do diretorio atual
diretorio_atual = os.path.dirname(os.path.abspath(__file__))

# Definindo as constantes
ARQUIVO_HISTORICO = os.path.join(diretorio_atual, '..', 'data', 'historico.csv')
LISTA_COLUNAS_ARQUIVO_HISTORICO = ["DataHora", "Operacao", "Valor", "Sinal"]
LIMITE_SAQUE = 500
LIMITE_SAQUES_POR_DIA = 3
LISTA_OPCOES_MENU = ["1","2","3","0"]

def menu_banco():

    try:
        # Criando o visual do menu
        menu = f"""
{" MENU ".center(22, "=")}
{"||":<20}||
{"|| [1] Depositar":<20}||
{"|| [2] Sacar":<20}||
{"|| [3] Extrato":<20}||
{"|| [0] Sair":<20}||
{"||":<20}||
{"".center(22, "=")}
Digite o número correspondente a umas das opções: """

        # Retornando o input do usuário
        return input(menu)
    
    except ValueError:
        print("Entrada inválida! Por favor, tente novamente.")
        return None

def registrar_historico(tipo, valor, sinal):
        
    # Obtendo data e hora atual
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    # Criando (caso não exista) ou abrindo o arquivo csv
    with open(ARQUIVO_HISTORICO, mode="a", newline="") as arquivo_csv:

        # Criando um objeto do tipo writer
        escritor_csv = csv.writer(arquivo_csv)

        # Verificando se o arquivo está vazio. Se sim, então adiciona os cabeçalhos
        if arquivo_csv.tell() == 0:
            escritor_csv.writerow(LISTA_COLUNAS_ARQUIVO_HISTORICO)

        # Escrevendo a operação no CSV
        escritor_csv.writerow([data_hora, tipo, f"{valor:.2f}",sinal])

def ler_historico():

    try:
        # Abrindo o arquivo csv
        with open(ARQUIVO_HISTORICO, mode="r") as arquivo_csv:
            
            # Lendo o histórico e convertendo em lista
            historico = list(csv.reader(arquivo_csv))

        return historico
    
    except FileNotFoundError:
        print("O histórico ainda não existe! Seu Saldo é R$ 0.00.")
        return []
    
def contar_saques_hoje(historico):

    # Obtendo a data de hoje
    hoje = datetime.now().strftime("%d/%m/%Y")

    # Verificando a quantidade de saques realizados na data de hoje
    saques_hoje = 0
    for linha in historico:
        data_operacao, tipo, valor, sinal = linha
        if tipo == "Saque" and data_operacao.startswith(hoje):
            saques_hoje += 1

    return saques_hoje

def obter_saldo():
    try:
        # Ler o arquivo CSV usando pandas
        df = pd.read_csv(ARQUIVO_HISTORICO)
        
        # Converter a coluna 'valor' para float
        df['Valor'] = df['Valor'].astype(float)
        
        # Calculando o Saldo
        saldo = sum(df['Valor'] * df['Sinal'])

    except FileNotFoundError:
        # Se o arquivo não for encontrado, o saldo é zero
        print("O histórico ainda não existe! Seu Saldo é R$ 0.00.")
        saldo = 0
    except pd.errors.EmptyDataError:
        # Se o arquivo estiver vazio, o saldo é zero
        print("O histórico está vazio. Seu Saldo é R$ 0.00.")
        saldo = 0
    except Exception as e:
        # Tratar outros possíveis erros
        print(f"Erro ao ler o arquivo de histórico: {e}")
        saldo = 0

    return saldo, df

def deposito():

    while True:
        try:
            # Obtendo o input do usuário
            valor = input("Digite o valor do depósito: ")

            # Verifica se o valor é um número float válido
            valor_float = float(valor)

            # Verifica se tem mais de duas casas decimais
            if "." in valor and len(valor.split(".")[-1]) > 2:
                print("O valor não pode ter mais de duas casas decimais. Tente novamente.")
                continue

            # Verifica se o valor é positivo
            if valor_float > 0:
                break
            else:
                print("O valor deve ser positivo. Tente novamente.")

        except ValueError:
            print("Entrada inválida! Por favor, digite um número válido.")

    # Registrando no histórico
    registrar_historico("Deposito", valor_float, 1)

    # Mensagem sucesso
    print(f"Depósito de R$ {valor_float:.2f} realizado com sucesso!")

def saque():

    # Lendo o histórico
    historico = ler_historico()

    if len(historico) == 0:
        return None

    # Calculando a quantidade de saques realizadas no dia de hoje
    saques_hoje = contar_saques_hoje(historico)

    # Verificando se o limite de saques foi atingido
    if saques_hoje >= LIMITE_SAQUES_POR_DIA:
        print(f"Limite de {LIMITE_SAQUES_POR_DIA} saques diários atingido!")
        return None
    
    # Obtendo o saldo
    saldo_atual,df = obter_saldo()

    while True:
        try:
            # Obtendo o input do usuário
            valor = input("Digite o valor do saque: ")

            # Verifica se o valor é um número float válido
            valor_float = float(valor)

            # Verificando o limite de saque
            if valor_float > LIMITE_SAQUE:
                print(f"O saque não maior que R$ {LIMITE_SAQUE}! Tente Novamente")
                continue

            # Verificando se o saldo é o sulficiente para o saque
            if valor_float > obter_saldo():
                print(f"O seu saldo atual é de R$ {saldo_atual:.2f}! Realize um saque válido.")
                continue

            # Verifica se tem mais de duas casas decimais
            if "." in valor and len(valor.split(".")[-1]) > 2:
                print("O valor não pode ter mais de duas casas decimais. Tente novamente.")
                continue

            # Verifica se o valor é positivo
            if valor_float > 0:
                break
            else:
                print("O valor deve ser positivo. Tente novamente.")

        except ValueError:
            print("Entrada inválida! Por favor, digite um número válido.")

    # Registrando no histórico
    registrar_historico('Saque', valor_float, -1)

    # Mensagem sucesso
    print(f"Saque de R$ {valor_float:.2f} registrado com sucesso!")

def extrato():

    saldo_atual,df = obter_saldo()

    if saldo_atual == 0:
        return 0
    
    saldo = obter_saldo()

    print(f"\nSaldo atual: R$ {saldo_atual:.2f}\n")

    # Ordena o DataFrame pela coluna 'DataHora' em ordem decrescente
    df = df.sort_values(by='DataHora', ascending=False)

    # Exibe o extrato ordenado
    print("Histórico de transações:")
    for index, row in df.iterrows():
        aux = "➖" if row['Operacao'] == "Saque" else "➕"
        print(f"{row['DataHora']} \t| {row['Operacao']} \t| {aux} R$ {float(row['Valor']):.2f}")

def main():

    while(True):

        # Disponibiliza o menu
        opcao = menu_banco()

        # Escolha inválida do usuário
        if opcao not in LISTA_OPCOES_MENU:
            print("\nOPÇÃO INVÁLIDA!\nDigite uma das opções disponíveis.")
            continue

        # Escolha da operação "depósito"
        elif opcao == "1":
            deposito()

        # Escolha da operação "saque"
        elif opcao == "2":
            saque()

        # Escolha da operação "extrato"
        elif opcao == "3":
            extrato()

        # Escolha da operação "sair"
        elif opcao == "0":
            break

if __name__ == "__main__":
    main()