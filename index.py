import redis

# Connessione a Redis
r = redis.Redis(host='localhost', port=6379, db=0)

# Funzione per caricare i dati iniziali in Redis
def load_initial_data():
    pollens = {
        "Milano": {"graminacee": "medio", "piante": "alto"},
        "Roma": {"graminacee": "alto", "piante": "critico"},
        "Napoli": {"graminacee": "basso", "piante": "medio"},
        "Palermo": {"graminacee": "critico", "piante": "basso"}
    }
    for city, levels in pollens.items():
        r.hset(city, mapping=levels)

# Funzione per ottenere i livelli di polline per una città
def get_pollen_levels(city):
    levels = r.hgetall(city)
    if not levels:
        return f"Città {city} non trovata nei dati."
    levels = {k.decode('utf-8'): v.decode('utf-8') for k, v in levels.items()}
    return levels

# Funzione per trovare la città con il livello peggiore per ogni tipo di polline
def get_worst_city():
    worst = {}
    allergeni = r.smembers("allergeni")
    allergeni = [allergene.decode('utf-8') for allergene in allergeni]

    for allergene in allergeni:
        max_level = None
        max_cities = []
        for city in r.keys():
            if city.decode('utf-8') == "allergeni":
                continue
            level = r.hget(city, allergene)
            if not level:
                continue
            level = level.decode('utf-8')
            if max_level is None or compare_levels(level, max_level) > 0:
                max_level = level
                max_cities = [city.decode('utf-8')]
            elif compare_levels(level, max_level) == 0:
                max_cities.append(city.decode('utf-8'))
        worst[allergene] = (max_level, max_cities)
    return worst

# Funzione per confrontare i livelli di polline
def compare_levels(level1, level2):
    levels_order = ["nullo", "basso", "medio", "alto", "critico"]
    return levels_order.index(level1) - levels_order.index(level2)

# Funzione per aggiungere una nuova città
def add_city(city, levels):
    r.hset(city, mapping=levels)
    print(f"Città {city} aggiunta con livelli {levels}.")

# Funzione per aggiungere un nuovo allergene
def add_allergene(allergene):
    r.sadd("allergeni", allergene)
    print(f"Allergene {allergene} aggiunto.")

# Funzione per aggiornare i livelli di polline di una città
def update_pollen_levels(city, levels):
    if not r.exists(city):
        print(f"Città {city} non trovata nei dati.")
        return
    r.hset(city, mapping=levels)
    print(f"Livelli di polline per {city} aggiornati a {levels}.")

if __name__ == "__main__":
    # Carica i dati iniziali
    load_initial_data()
    r.sadd("allergeni", "graminacee", "piante")

    while True:
        print("1. Visualizza livelli di polline per una città")
        print("2. Aggiungi una nuova città")
        print("3. Aggiungi un nuovo allergene")
        print("4. Aggiorna livelli di polline per una città")
        print("5. Visualizza la città con il peggior livello di polline")
        print("6. Esci")
        menu = input("Scegli un'opzione: ").strip()

        if menu == "1":
            city = input("Inserisci una città: ").strip()
            levels = get_pollen_levels(city)
            if isinstance(levels, str):
                print(levels)
            else:
                print(f"Livelli di polline per {city}:")
                for allergene, level in levels.items():
                    print(f"{allergene.capitalize()}: {level}")

        elif menu == "2":
            city = input("Inserisci il nome della città: ").strip()
            levels = {}
            for allergene in r.smembers("allergeni"):
                allergene = allergene.decode('utf-8')
                level = input(f"Inserisci il livello di {allergene} per {city} (nullo, basso, medio, alto, critico): ").strip()
                levels[allergene] = level
            add_city(city, levels)

        elif menu == "3":
            allergene = input("Inserisci il nome del nuovo allergene: ").strip()
            add_allergene(allergene)

        elif menu == "4":
            city = input("Inserisci il nome della città: ").strip()
            if not r.exists(city):
                print(f"Città {city} non trovata nei dati.")
                continue
            levels = {}
            for allergene in r.smembers("allergeni"):
                allergene = allergene.decode('utf-8')
                level = input(f"Inserisci il nuovo livello di {allergene} per {city} (nullo, basso, medio, alto, critico): ").strip()
                levels[allergene] = level
            update_pollen_levels(city, levels)

        elif menu == "5":
            worst_cities = get_worst_city()
            print("\nCittà con i peggiori livelli di polline:")
            for allergene, (level, cities) in worst_cities.items():
                print(f"{allergene.capitalize()}: {level} in {', '.join(cities)}")

        elif menu == "6":
            break

        else:
            print("Opzione non valida. Riprova.")
