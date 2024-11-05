from cryptography.fernet import Fernet
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import pymongo
import hashlib
import datetime
import json

def gerar_hash(senha):
    hash_obj = hashlib.sha256(senha.encode())
    return hash_obj.hexdigest()

def conectarbanco():
    uri = "mongodb+srv://gabriellhenriquee1901:INJBIp9UmcxK0ykS@cluster0.5bvhs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    cliente = MongoClient(uri)
    db = cliente['Consultorio']
    global colecao 
    global colecao2
    global colecao3
    colecao = db['Doutor(a)']
    colecao2 = db['Paciente']
    colecao3 = db['Compartilhamentos']
    try:
        cliente.admin.command('ping')
        print("Conectado ao MongoDB!")
    except Exception as e:
        print(f"Erro ao conectar: {e}")

def login():
    while(True):
        try:
            CRM = int(input("Digite o Seu CRM:\n"))
            logsenha = 0
            for item in colecao.find({'CRM': CRM}):
                logsenha = item['Senha']  
                global idM
                idM = item['_id']
            if logsenha is None:
                print("CRM não encontrado.")
                return 0  
            senha = input("Digite a Sua Senha:")
            hash_senha = gerar_hash(senha)
            if hash_senha == logsenha:
                return 1 
            else:
                print("Senha ou CRM Incorretos...!")
        except:
            print("Dado Incorreto, Favor tente novamente!")

def Regist():
    while(True):
        try:    
            Nome = input("Qual o Nome do Paciente:")
            Idade = int(input("Qual a Idade do Paciente:"))
            Relatorio = input("Qual o Relatorio do Paciente:")
            Tratamento = input("Qual o Tratamento indicado para o paciente:")
            maior_id = None
            chave = Fernet.generate_key()
            fernet = Fernet(chave)
            Paciente = {"Nome":Nome,"Idade":Idade,"Relatorio":Relatorio,"Tratamento":Tratamento,"Chave":chave.decode()}
            Paciente_json = json.dumps(Paciente)
            PacienteCrip = fernet.encrypt(Paciente_json.encode())
            for item in colecao2.find():
                if maior_id is None or item['_id'] > maior_id:
                    maior_id = item['_id'] 
            maior_id = maior_id+1
            Pacient = {"Criptografia":PacienteCrip,"_id":maior_id}
            p = colecao2.insert_one(Pacient)
            print(f"\nPaciente Registrado com Sucesso.\nid:{maior_id}\nChave para Descripitografia:{chave.decode()}")
            break

        except:
            print("Ocorreu algum erro ao realizar o registro")
      
def Descripto():
    while(True):
        try:
            idr = int(input("Digite o id do Paciente:"))
            chaver = input("Digite a Chave para a Descripitografia:")
            fernet = Fernet(chaver)
            for item in colecao2.find({'_id': idr}):
                cripitografia = item['Criptografia']
                mensagem_descriptografada = fernet.decrypt(cripitografia).decode()
                mensagem_descriptografada = json.loads(mensagem_descriptografada)
                print(f'Nome do Paciente: {mensagem_descriptografada["Nome"]}')
                print(f"Idade: {mensagem_descriptografada['Idade']}")
                print(f"Relatório: {mensagem_descriptografada['Relatorio']}")
                print(f"Tratamento: {mensagem_descriptografada['Tratamento']}")
                resp = int(input("Deseja Gerar um Chave Temporaria para que outros medicos acessem?(1-Sim 2-Não)\n"))
                if resp == 1:
                    while(True):
                        resp2 = int(input("Digite o Dia de validade:"))
                        resp3 = int(input("Digite o Mes de Validade:"))
                        resp4 = int(input("Digite o Ano de Validade:"))
                        if resp2 < 1 or resp2 > 30:
                            print("Valor Invalido! Apenas Valores Maiores de 1 e menores de 30")
                        if resp3 < 1 or resp3 > 12:
                            print("Valor Invalido! Apenas Valores Maiores de 1 e menores de 12")
                        if resp4 < 0:
                            print("Valor Invalido! Apenas Valores Maiores de 1")
                        maior_id = None
                        chave = Fernet.generate_key()
                        fernet = Fernet(chave)
                        Paciente = {"Nome":mensagem_descriptografada["Nome"],"Idade":mensagem_descriptografada["Idade"],"Relatorio":mensagem_descriptografada['Relatorio'],"Tratamento":mensagem_descriptografada['Tratamento'],"Chave":chave.decode()}
                        Paciente_json = json.dumps(Paciente)
                        PacienteCrip = fernet.encrypt(Paciente_json.encode())
                        Pacient = {"Criptografia":PacienteCrip,"_id":idr,"Dia":resp2,"Mes":resp3,"Ano":resp4}
                        p = colecao3.insert_one(Pacient)
                        print(f"\nPaciente Registrado com Sucesso.\nid:{idr}\nChave para Descripitografia:{chave.decode()}")
                        break
                return 
        except:
            print("Ocorreu Algum Problema no Envio dos Dados!")
def MRegist():
    while(True):
        try:
            Crm = int(input("Qual o CRM do Medico a Ser Registrado:"))
            if len(str(Crm)) < 6 or len(str(Crm)) > 6:
                print("O Crm do Medico Deve Conter 6 Digitos")
            else:
                Nome = input("Qual o Nome do Medico:")
                Senha = input("Cadastre um Senha para Login's Futuros:")
                maior_id = None
                stringhash = hashlib.sha256(Senha.encode()).hexdigest()
                for item in colecao.find():
                            if maior_id is None or item['_id'] > maior_id:
                                maior_id = item['_id'] 
                maior_id = maior_id+1
                Pacient = {"Nome":Nome,"_id":maior_id,"CRM":Crm,"Senha":stringhash}
                p = colecao.insert_one(Pacient)
                print("Médico Cadastrado Com Sucesso!!")
                return
        except:
            print("Ocorreu um Erro no Registro!")

def ComResgist():
    while(True):
        try:
            data_atual = datetime.datetime.now()
            dia = data_atual.day
            mes = data_atual.month
            ano = data_atual.year
            idr = int(input("Digite o id do Paciente:"))
            for item in colecao3.find({'_id': idr}):
                dia1 = item['Dia']
                mes1 = item['Mes']
                ano1 = item['Ano']
            if ano > ano1:
                print("Esse Registro Já Foi Inspirado")
                return
            elif mes > mes1:
                print("Esse Registro Já Foi Inspirado")
                return
            elif dia > dia1:
                print("Esse Registro Já Foi Inspirado")
                return    
            chaver = input("Digite a Chave para a Descripitografia:")
            fernet = Fernet(chaver)
            for item in colecao3.find({'_id': idr}):
                cripitografia = item['Criptografia']
                mensagem_descriptografada = fernet.decrypt(cripitografia).decode()
                mensagem_descriptografada = json.loads(mensagem_descriptografada)
                print(f'Nome do Paciente: {mensagem_descriptografada["Nome"]}')
                print(f"Idade: {mensagem_descriptografada['Idade']}")
                print(f"Relatório: {mensagem_descriptografada['Relatorio']}")
                print(f"Tratamento: {mensagem_descriptografada['Tratamento']}")
        except:
            print("Verifique os Valores Digitados")

conectarbanco()


if login() == 1:
            print("Login Efetuado Com Sucesso!!\n\nOque deseja fazer Agora?")
            while(True):
                try:
                    if idM == 1:
                        resp = int(input("\n0-Registrar um Novo Medico\n1-Registrar Dados De um Paciente\n2-Abrir Registro de Pacientes\n3-Abrir Registro Compartilhado\n4-Sair do Programa\n"))
                    else:
                        resp = int(input("\n1-Registrar Dados De um Paciente\n2-Abrir Registro de Pacientes\n3-Abrir Registro Compartilhado\n4-Sair do Programa\n"))
                    if resp == 0 and idM == 1:
                        MRegist()
                    if resp == 1:
                        Regist()
                    if resp == 2:
                        Descripto()
                    if resp == 3:
                        ComResgist()
                    if resp == 4:
                        exit()
                except TypeError:
                    print("Verifique os Dados Digitados")
                except ValueError:
                    print("Verifique os Dados Digitados")
else:
    print("Ocorreu Algum Erro ao Tentar logar!")
