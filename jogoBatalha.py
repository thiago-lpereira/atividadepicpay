import psycopg2

def connect_db():
    return psycopg2.connect(
        dbname="dbGame",
        user="avnadmin",
        password="AVNS_I2YSg3hf2GFrMM8X7eZ",
        host="pg-126b320f-ncgaloni-ec04.d.aivencloud.com",
        port="21577"
    )

def create_jogador(conn, nome, apelido, nivel, classe):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO jogadores (nome, apelido, nivel, classe)
            VALUES (%s, %s, %s, %s) RETURNING jogador_id;
        """, (nome, apelido, nivel, classe))
        conn.commit()
        return cur.fetchone()[0]

def create_personagem(conn, jogador_id, nome, vida=100, ataque=10, defesa=5):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO personagens (jogador_id, nome, vida, ataque, defesa)
            VALUES (%s, %s, %s, %s, %s) RETURNING personagem_id;
        """, (jogador_id, nome, vida, ataque, defesa))
        conn.commit()
        return cur.fetchone()[0]

def get_jogadores(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM jogadores;")
        return cur.fetchall()

def get_personagens(conn, jogador_id):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM personagens WHERE jogador_id = %s;", (jogador_id,))
        return cur.fetchall()

def iniciar_batalha(conn, atacante_id, defensor_id):
    with conn.cursor() as cur:
        # Simula uma batalha simples
        cur.execute("SELECT ataque, defesa FROM personagens WHERE personagem_id = %s;", (atacante_id,))
        atacante = cur.fetchone()
        cur.execute("SELECT ataque, defesa FROM personagens WHERE personagem_id = %s;", (defensor_id,))
        defensor = cur.fetchone()

        ataque_liquido = atacante[0] - defensor[1]
        vitoria = ataque_liquido > 0

        recompensa = ataque_liquido * 10 if vitoria else ataque_liquido * 5

        if vitoria:
            cur.execute("""
                update personagens set vida=vida - %s where personagem_id = %s;
            """, (ataque_liquido, defensor_id))
            cur.execute("""
                update personagens set vida=vida + %s where personagem_id = %s;
            """, (ataque_liquido, atacante_id))
        else:
            cur.execute("""
                update personagens set vida=vida + %s where personagem_id = %s;
            """, (ataque_liquido, defensor_id))
            cur.execute("""
                update personagens set vida=vida - %s where personagem_id = %s;
            """, (ataque_liquido, atacante_id))

        cur.execute("""
            INSERT INTO batalhas (atacante_id, defensor_id, vitoria, recompensa)
            VALUES (%s, %s, %s, %s) RETURNING batalha_id;
        """, (atacante_id, defensor_id, vitoria, recompensa))
       
        conn.commit()
        return cur.fetchone()[0], vitoria, recompensa

def main():
    conn = connect_db()
    print("Bem-vindo ao jogo de batalha!")
    
    while True:
        print("\n1. Listar jogadores")
        print("2. Adicionar jogador")
        print("3. Listar personagens de um jogador")
        print("4. Listar Iventario personagem")
        print("5. Adicionar personagem")
        print("6. Adicionar inventario")
        print("7. Iniciar batalha")
        print("0. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            jogadores = get_jogadores(conn)
            print("(jogador_id, jogador_id, nome, apelido, nivel, classe")
            for jogador in jogadores:
                print(jogador)
        elif escolha == '2':
            nome = input("Nome: ")
            apelido = input("Apelido: ")
            nivel = int(input("Nível: "))
            classe = input("Classe: ")
            jogador_id = create_jogador(conn, nome, apelido, nivel, classe)
            print(f"Jogador criado com ID {jogador_id}")
        elif escolha == '3':
            jogador_id = int(input("ID do jogador: "))
            personagens = get_personagens(conn, jogador_id)
            print("(personagem_id, jogador_id, nome, vida, ataque, defesa)")
            for personagem in personagens:
                print(personagem)
        elif escolha == '4':
            print("Precisa desenvolver essa funcionalidade")
        elif escolha == '5':
            jogador_id = int(input("ID do jogador: "))
            nome = input("Nome do personagem: ")
            vida = int(input("Vida: "))
            ataque = int(input("Ataque: "))
            defesa = int(input("Defesa: "))
            personagem_id = create_personagem(conn, jogador_id, nome, vida, ataque, defesa)
            print(f"Personagem criado com ID {personagem_id}")
        elif escolha == '6':
            print("Precisa desenvolver essa funcionalidade")
        elif escolha == '7':
            atacante_id = int(input("ID do atacante: "))
            defensor_id = int(input("ID do defensor: "))
            batalha_id, vitoria, recompensa = iniciar_batalha(conn, atacante_id, defensor_id)
            resultado = "vitoria" if vitoria else "derrota"
            print(f"Batalha {batalha_id} terminou em {resultado}. Recompensa: {recompensa}")
        elif escolha == '0':
            break
        else:
            print("Opção inválida, tente novamente.")
    
    conn.close()

if __name__ == "__main__":
    main()

