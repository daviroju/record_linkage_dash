import pandas as pd
import random
import faker
import os

fake = faker.Faker("pt_BR")
faker.Faker.seed(42)
random.seed(42)

def gerar_cpf():
    cpf = [random.randint(0, 9) for _ in range(9)]

    soma = sum([(10 - i) * cpf[i] for i in range(9)])
    d1 = (soma * 10 % 11) % 10
    cpf.append(d1)

    soma = sum([(11 - i) * cpf[i] for i in range(10)])
    d2 = (soma * 10 % 11) % 10
    cpf.append(d2)

    return "".join(map(str, cpf))


def perturbar_texto(texto):
    if random.random() < 0.2:
        pos = random.randint(0, len(texto) - 1)
        letra_errada = random.choice("abcdefghijklmnopqrstuvwxyz")
        return texto[:pos] + letra_errada + texto[pos+1:]
    return texto


def gerar_dataframe(n_linhas: int, id_inicio: int = 1):
    dados = []
    for i in range(n_linhas):
        if i % 2 == 0:
            nome = fake.first_name_male() + " " + fake.last_name_male()
            sexo = "M"
        else:
            nome = fake.first_name_female() + " " + fake.last_name_female()
            sexo = "F"

        nome_mae = fake.first_name_female() + " " + fake.last_name_female()

        data_nasc = fake.date_of_birth(
            minimum_age=18, maximum_age=80
        ).strftime("%Y-%m-%d")

        cpf = gerar_cpf()

        dados.append({
            "id": id_inicio + i,
            "nome": perturbar_texto(nome),
            "nome_mae": perturbar_texto(nome_mae),
            "data_nascimento": data_nasc,
            "sexo": sexo,
            "numero_cpf": cpf
        })
    return pd.DataFrame(dados)