# -*- coding: utf-8 -*-

""" Bataille navale """

# Auteur : Nicolas Vincent T°S5

import sys
import math
from itertools import product
import random
import string

objectsj1 = []  # Tableau contenant les objets du plateau du joueur 1
objectsj2 = []  # Tableau contenant les objets du plateau du joueur 2

config = dict()  # Fichier de configuration


def read_config():
    """ Lit le fichier de configuration config.txt """

    try:
        with open("config.txt", 'r') as f:
            print("\nFichier contenant la configuration :", f.name)
            data = f.read()
    except:
        f = open("config.txt", "w")
        f.close()

    config_list = []
    print("Configurations présentes dans le fichier.")
    for line in data.splitlines():
        print(eval(line))  # str to list
        config_list.append(eval(line))

    # print(config_list) # Liste de tuples
    return config_list


def configuration():
    """Cré un fichier texte de configuration contenant la taille du plateau ainsi que
         le nombre de bateaux avec leur taille."""

    # Tests des inputs du nb_lines,nb_columns, nb_bateaux
    while True:
        try:
            columns = int(input('Entrer le nombre de colones (10-26): '))
            if columns > 26 or columns < 10:
                raise ValueError("Entrer un entier compris entre 10 et 26.")
            break
        except ValueError as VE:
            print(VE)

    config["columns"] = columns

    while True:
        try:
            lines = int(input('Entrer le nombre de lignes (10-26): '))
            if lines > 26 or lines < 10:
                raise ValueError("Entrer un entier compris entre 10 et 26.")
            break
        except ValueError as VE:
            print(VE)

    config["lines"] = lines

    while True:
        try:
            ships_values = list(map(int, input(
                'Entrer à la suite les nombres de bateaux de tailles 2,3,4 et 5 séparés par une virgule : ').split(',')))
            # print(ships_values)

            # Test de l'input
            if len(ships_values) != 4:
                raise ValueError("Entrer 4 valeurs séparées par des virgules.")
            # Validation de l'input
            verif = input("Valider la sélection (O/N): ")
            if not verif in ["O", "N"]:
                raise ValueError("Entrer 0 ou N.")
            if verif == "N":
                continue

            # Test d'un nombre de bateaux valide
            nb_tot_ships = sum([i for i in ships_values])
            # print(nb_tot_ships)
            nb_ships_allowed = ships_rules(config)
            if nb_tot_ships > nb_ships_allowed:
                raise ValueError(
                    "Vous avez entré un nombre total de bateaux trop élevé par rapport à la taille du plateau.")

            # Vérification qu'il n'y a pas nb_ships_taille_sup >
            # nb_ships_taille_inf.
            for i in range(len(ships_values) - 1):
                if ships_values[i] < ships_values[i + 1]:
                    raise ValueError(
                        "Vous avez plus de bateaux de taille {} que de bateaux de taille {}.".format(i + 3, i + 2))
            break
        except ValueError as VE:
            print(VE)

    ships = {5: ships_values[3], 4: ships_values[2], 3: ships_values[
        1], 2: ships_values[0]}  # taille : nombre

    config["ships"] = ships

    # On trie le dictionnaire de configuration
    config_sorted = sorted(config.items(), key=lambda t: t[0])

    config_list = read_config()  # Lit le fichier de configuration

    if not config_sorted in config_list:  # Si la config n'est pas déjà présente, on l'écrit
        with open("config.txt", 'a') as f:
            f.write(str(config_sorted) + '\n')

    # Afficher config
    print("Contenu du fichier de configuration généré : ")
    for cle, valeur in config.items():
        print(cle, ':', valeur)

    return nb_tot_ships


class Case(object):

    """ Classe repésentant une case du plateau
     - tableau d'objets : coordonnées, notre bateau, tir de l'adversaire, tir que nous avons effectué, bateau adverse touché
    """

    def __init__(self):
        self.coordonnees = 0
        self.our_tir = False
        self.adv_tir = False
        self.our_ship = 0
        self.adv_ship = False

    def __str__(self):
        return "Coordonnées : {}, Tir effectué : {}, Tir reçu : {}, Bateau présent : {}, Bateau de l'adversaire : {}\n".format(
            self.coordonnees, self.our_tir, self.adv_tir, self.our_ship, self.adv_ship)

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, name):
        """
            Est appelée quand on demande un attribut appelé "name" et qu'il
            n'existe pas.
        """
        return None

    def __delattr__(self, nom_attr):
        """
            On ne peut supprimer d'attribut, on lève l'exception
            AttributeError
        """
        raise AttributeError(
            "Vous ne pouvez supprimer aucun attribut de cette classe")


class Player(object):

    """ Classe représentant un joueur """

    def __init__(self):
        self.name = 'IA'
        self.plateau = None
        self.start = False  # Commencé ou non la partie
        self.tir = 0  # Nb tirs effectués
        self.ships_left = 5  # 5 bateaux restant (bataille navale classique)
        self.ships_lose = 0  # 0 bateaux coulé
        self.ships_hit = 0  # 0 case bateau touché

    def __str__(self):
        return "Nom : {}\nPlateau : {}\nA commencé la partie : {}\nNombre de tirs effectués : {}\nNombre de bateaux restant : {}\nNombre de bateaux coulés : {}\nNombre de cases bateau touchées : {}".format(
            self.name, self.plateau, self.start, self.tir, self.ships_left, self.ships_lose, self.ships_hit)

    def __getattr__(self, name):
        """
            Est appelée quand on demande un attribut appelé "name" et qu'il
            n'existe pas.
        """
        return None

    def __delattr__(self, nom_attr):
        """
            On ne peut supprimer d'attribut, on lève l'exception
            AttributeError
        """
        raise AttributeError(
            "Vous ne pouvez supprimer aucun attribut de cette classe")


def plateau(objects, config):
    """ Cré un plateau de jeu pouvant aller jusqu'à 26*26 cases
    - Ordonnées : A - Z
    - Abscisses : 0 - 26
    """

    # Génération des coordonnées :
    ordonnes = ''
    abscisses = ''
    # Lettres de l'alphabet en ordonnée selon le nb de lignes voulues
    ordonnes = list(string.ascii_uppercase[:config["lines"]])
    # En abscisse les chiffres correspondant
    abscisses = [str(i) for i in range(config["columns"])]

    # print(ordonnes,abscisses)

    table = []  # Initialise une liste vide qui contiendra les coordonnées

    # On réalise les couples
    table = list(product(ordonnes, abscisses))

    # On transforme les couples en string
    for i in range(len(table)):
        table[i] = "".join(table[i])

    # Affichage des coordonnées
    for i in range(0, config["lines"] * config["columns"], config["columns"]):
        print(table[i:i + config["columns"]])

    # Affichage des objets
    for i in range(config["lines"] * config["columns"]):
        objects.append('case' + str(i))
        objects[i] = Case()
        objects[i].coordonnees = table[i]
        # print(objects[i])

    return table


def test_directions(objects, config, taille, direction, i):
    """ Test de si le bateau se trouve hors plateau
    :: objects : objet représentant une case
    :: config : fichier de configuration
    :: direction : direction du bateau
    :: taille : taille du bateau
    :: i : emplacement initial du bateau
    """

    if direction == 'N':
        try:
            return - config["columns"], objects[(i - config["columns"] * (taille - 1)) % (
                config["columns"] * config["lines"])].coordonnees > objects[i].coordonnees
        except:
            return - config["columns"], objects[(i - config["columns"] * (taille - 1)) % (
                config["columns"] * config["lines"])]["coordonnees"] > objects[i]["coordonnees"]
    elif direction == 'S':
        try:
            return config["columns"], objects[(i + config["columns"] * (taille - 1)) % (
                config["columns"] * config["lines"])].coordonnees < objects[i].coordonnees
        except:
            return config["columns"], objects[(i + config["columns"] * (taille - 1)) % (
                config["columns"] * config["lines"])]["coordonnees"] < objects[i]["coordonnees"]
    elif direction == 'E':
        try:
            return 1, objects[(i + taille - 1) % (config["columns"] *
                                                  config["lines"])].coordonnees[0] != objects[i].coordonnees[0]
        except:
            return 1, objects[(i + taille - 1) % (config["columns"] * config["lines"])][
                "coordonnees"][0] != objects[i]["coordonnees"][0]
    elif direction == 'O':
        try:
            return - 1, objects[(i - (taille - 1)) % (config["columns"] *
                                                      config["lines"])].coordonnees[0] != objects[i].coordonnees[0]
        except:
            return - 1, objects[(i - (taille - 1)) % (config["columns"] * config["lines"])][
                "coordonnees"][0] != objects[i]["coordonnees"][0]


def placement_joueur_sub(objects, config, taille,
                         direction, i, restart, placed, aléatoire):
    """ Placement avec prise en compte de la direction si les conditions sont vérifiées
    :: objects : objet représentant une case
    :: config : fichier de configuration
    :: direction : direction du bateau
    :: taille : taille du bateau
    :: i : emplacement initial du bateau
    :: restart : recommencer la boucle
    :: placed : bateau complet placé
    :: aléatoire : placement aléatoire ou non
    """

    for j in range(taille):
        # Si on sort du plateau
        if test_directions(objects, config, taille, direction, i)[1]:
            if not aléatoire:
                print("Votre bateau sort du plateau.")
            restart = True
            break
        elif objects[i + test_directions(objects, config, taille, direction, i)[0] * j].our_ship != 0:
            if not aléatoire:
                print("Un bateau se trouve déjà à cet emplacement.")
            while j != 0:
                j -= 1
                objects[
                    i + test_directions(objects, config, taille, direction, i)[0] * j].our_ship = 0
            placed = False
            restart = True
            break
        # On place le bateau
        objects[i + test_directions(objects, config,
                                    taille, direction, i)[0] * j].our_ship = taille
        placed = True

    return restart, placed, objects


def placement_joueur(objects, nb_tot_ships, config,
                     table, aléatoire=False, near=True):
    """ Emplacement des bateaux
    - Aléatoire
    - choisi par le joueur : demander une première case, la taille du bateau puis la direction (Nord/Est/Sud/Ouest)
    :: objects : objet représentant une case
    :: nb_tot_ships ""
    :: config : fichier de configuration
    :: table : tableau des coordonnées
    :: near : bateaux côtes à côtes
    """

    restant = sum([i for i in config["ships"].values()])
    # Variable modifiable sans interférer avec config
    configships = config["ships"].copy()

    taille_list = []
    for i in configships.keys():
        while taille_list.count(i) != configships[i]:
            taille_list.append(i)

    for k in range(nb_tot_ships):  # nb_total_bateaux
        restart = True
        while restart:  # Boucle infini pour répéter lsq'il y a une mauvaise entrée ou un bateau déjà présent
            restart = False
            placed = False  # Variable True si un bateau complet à été placé
            if aléatoire == True:
                taille, place, direction, configships, taille_list = alea_input_rules(
                    configships, table, taille_list)
            else:
                taille, place, direction, configships = user_input_rules(
                    configships, table)
            for i in range(len(objects)):  # Parcours de la liste d'objets
                coordonnees = objects[i].coordonnees
                if coordonnees == place:  # Si on arrive aux coordonnées entrées
                    # Liste des cases autour du bateau (test présence bateau)
                    cases_autour_boat = near_cases(
                        objects, config, taille, direction, i, coordonnees)
                    if near == False and (len(cases_autour_boat) != cases_autour_boat.count(
                            0) + cases_autour_boat.count(taille) or cases_autour_boat.count(taille) > taille):
                        placed = False
                        restart = True
                        break
                    restart, placed, objects = placement_joueur_sub(
                        objects, config, taille, direction, i, restart, placed, aléatoire)
                    if placed:
                        # On décrémente de 1 le nb de bateaux de cette
                        # taille
                        configships[taille] -= 1
                        restant -= 1
                        if not aléatoire:
                            print("Votre bateau est bien placé.")
                            print("Il vous reste {} bateaux de taille {}.".format(
                                configships[taille], taille))
                            print(
                                "Il vous reste {} bateaux à placer.".format(restant))


def near_cases(objects, config, taille, direction, i, coordonnees):
    """ Retourne une liste de la présence de bateaux sur les cases adjacentes d'un bateau en prennant en compte le bateau lui-même
    :: objects : objet représentant une case
    :: config : fichier de configuration
    :: direction : direction du bateau
    :: taille : taille du bateau
    :: i : emplacement initial du bateau
    """

    cases_autour_boat = []

    for j in range(taille + 2):
        cases_autour_boat.extend(near_cases_sub(
            objects, config, i + test_directions(objects, config, taille, direction, i)[0] * j))

    # print(cases_autour_boat)
    return cases_autour_boat


def near_cases_sub(objects, config, place):
    """ Regarde s'il y a des bateaux sur les cases adjacentes d'une case
    :: objects : objet représentant une case
    :: config : fichier de configuration
    :: place : emplacement du bateau
    """

    cases_autour = []

    for i in [- config["columns"], config["columns"], - 1, 1]:
        try:
            cases_autour.append(objects[place + i].our_ship)
        except:
            cases_autour.append(0)

    # print(cases_autour)
    return cases_autour


def play(joueur1, joueur2, table, aléatoire=False):
    """ Jeu tour par tour
    :: joueur1, joueur2 : 2 adversaires
    :: table : tableau des coordonnées
    :: aléatoire : True si on est contre l'IA
    """

    # Mise en place du joueur qui commence la partie
    if joueur1.start == True:
        first = joueur1
        second = joueur2
    elif joueur2.start == True:
        first = joueur2
        second = joueur1

    altern_joueur = [first, second]

    # Paramètres stratégie_IA
    horizontal = False
    vertical = False
    possibilites = []  # Tableau des cases où se trouve un bateau adverse
    table_allowed = table.copy()
    direct = ['N', 'S', 'E', 'O']

    # Boucle globale
    n = 0
    while joueur1.ships_left != 0 or joueur2.ships_left != 0:
        directions = direct.copy()
        while True:
            try:
                if aléatoire == True and n % 2 == altern_joueur.index(joueur2):
                    joueur1, joueur2, position, table_allowed, horizontal, vertical, directions = strategie_IA(
                        joueur1, joueur2, table_allowed, config, possibilites, horizontal, vertical, directions, direct)
                else:
                    position = input("Entrer la case cible de votre tir : ")
                if not position in table:
                    raise ValueError(
                        "Entrer une case qui est présente sur le plateau.")
                for i in range(len(altern_joueur[n % 2].plateau)):
                    if altern_joueur[n % 2].plateau[
                            i]['coordonnees'] == position:
                        if altern_joueur[n % 2].plateau[i]['our_tir'] == False:
                            # 1 tir de plus effectué
                            altern_joueur[n % 2].tir += 1
                            # Emplacement sur lequel on a tiré
                            altern_joueur[n % 2].plateau[i]['our_tir'] = True
                            altern_joueur[(n + 1) %
                                          2].plateau[i]['adv_tir'] = True
                            # Test présence d'un bateau
                            if altern_joueur[(n + 1) %
                                             2].plateau[i]['our_ship'] != 0:
                                altern_joueur[n % 2].plateau[
                                    i]['adv_ship'] = True
                                altern_joueur[n % 2].ships_hit += 1
                        elif altern_joueur[n % 2].plateau[i]['our_tir'] == True:
                            raise ValueError(
                                "Vous avez déjà tiré sur cette position.")
                break
            except ValueError as VE:
                print(VE)

    # Test bateau coulé
    # Si aucune case bateau autour --> bateau coulé
    # While sur une même droite
    # Si mêmes chiffres avec adv_tir --> bateau coulé
    # Quand on connaît la taille du bateau attaqué, adv_ships = taille
        n += 1


def strategie_IA(joueur1, joueur2, table_allowed, config,
                 possibilites, horizontal, vertical, directions, direct):
    """ Stratégie de jeu de l'IA: un bateau à la fois
    :: joueur2 : IA
    :: table : tableau des coordonnées
    :: config : fichier de configuration
    Recherche de bateaux sur les cases adjacentes si case bateau touchée
    Quand trouvé, continuer sur la même ligne
    Quand il n'y en a plus, s'arrêter : passer de l'autre côté ou retourner aléatoire si bateau coulé
    """

    restart = True
    while restart:  # Boucle infini pour répéter lsq'il y a une mauvaise entrée ou un bateau déjà présent
        restart = False

        possibilites = [i for i in range(len(joueur2.plateau)) if joueur2.plateau[i][
            'adv_ship'] == True and i not in possibilites]
        print(possibilites)

        boat = [joueur1.plateau[i]['our_ship']
                for i in range(len(joueur1.plateau)) if i in possibilites]
        print(boat)

        # Test même valeur dans boat
        if boat and boat.count(boat[0]) == boat[0]:  # (2,2,3,3) : nb 2 = 2
            joueur1.ships_left -= 1
            joueur1.ships_lose += 1
            horizontal, vertical = False, False
            # All index of the first value
            for i in [i for i, val in enumerate(boat) if val == boat[0]]:
                # Emplacement dans possibilites des valeurs puis remplacement
                # valeurs dans joueur2.plateau
                joueur2.plateau[possibilites[0]]['adv_ship'] = boat[0]
                # print(joueur2.plateau[possibilites[0]]['adv_ship'])
                possibilites.remove(possibilites[0])
                # print(possibilites)

        # Test deux cases bateau adjacentes
        possibilites.sort()
        for x, y in zip(possibilites, possibilites[1:]):
            print(x, y)
            if x + 1 == y:
                horizontal = True
            elif x + config["columns"] == y:
                vertical = True
            else:
                horizontal, vertical = False, False

        print(horizontal, vertical)

        if not possibilites:  # Test liste vide
            position = random.choice(table_allowed)
            print(position)
        elif len(possibilites) == 1:  # Test 1 seul élément
            direction = random.choice(directions)
        elif horizontal:  # Test 2 éléments côtes à côtes
            direction = random.choice(direct[2:])
        elif vertical:  # Test 2 éléments l'un en dessous de l'autre
            direction = random.choice(direct[:2])

        if possibilites:
            if (joueur2.plateau[(possibilites[0] - 1) % (config["columns"] * config["lines"])]['coordonnees'] not in table_allowed and horizontal) or (
                    joueur2.plateau[(possibilites[0] - config["columns"]) % (config["columns"] * config["lines"])]['coordonnees'] not in table_allowed and vertical):
                case_bateau = possibilites[-1]
                print("g H")
            elif (joueur2.plateau[(possibilites[-1] + 1) % (config["columns"] * config["lines"])]['coordonnees'] not in table_allowed and horizontal) or (joueur2.plateau[(possibilites[-1] + config["columns"]) % (config["columns"] * config["lines"])]['coordonnees'] not in table_allowed and vertical):
                case_bateau = possibilites[0]
                print("b d")
            else:
                case_bateau = random.choice(
                    [possibilites[0], possibilites[-1]])
            print(case_bateau)
            if case_bateau == possibilites[0] and horizontal:
                direction = direct[3]
            elif case_bateau == possibilites[0] and vertical:
                direction = direct[0]
            elif case_bateau == possibilites[-1] and horizontal:
                direction = direct[2]
            elif case_bateau == possibilites[-1] and vertical:
                direction = direct[1]
            print(direction)
            # Si on ne sort pas du plateau
            if not test_directions(
                    joueur2.plateau, config, 2, direction, case_bateau)[1]:
                position = joueur2.plateau[case_bateau + test_directions(
                    joueur2.plateau, config, 2, direction, case_bateau)[0]]['coordonnees']
                print(position)
                if direction in directions:
                    directions.remove(direction)
            else:
                restart = True
                continue
            print(directions)

        if position in table_allowed:
            # (34,35,36) si case_bateau = 34 et que direction = E, la position 35 n'est déjà plus dans table_allowed, on passe à l'autre case_bateau
            table_allowed.remove(position)
        else:
            restart = True
            continue

        print(table_allowed)

    return joueur1, joueur2, position, table_allowed, horizontal, vertical, directions


def choose_starter(joueur1, joueur2):
    """ Choix de qui commence
    Aléatoire, joueur1, joueur2
    :: joueur1, joueur2 : 2 adversaires
    """

    while True:
        try:
            start = input(
                "Choisissez qui commence la partie (1, 2, A): ")
            if not start in ['1', '2', 'A']:
                raise ValueError("Entrer 1, 2 ou A.")
            if start == 'A':
                start = random.choice(['1', '2'])
            break
        except ValueError as VE:
            print(VE)

    if start == '1':
        joueur1.start = True
        print("{joueur1} commence la partie.".format(joueur1=joueur1.name))
    elif start == '2':
        joueur2.start = True
        print("{joueur2} commence la partie.".format(joueur2=joueur2.name))

    return joueur1, joueur2


def affichage_our_ships(objects, config):
    """ Affichage des bateaux du joueur (+ attaques ennemi)
    :: config : fichier de configuration
    :: objects : plateau
    """

    j_ships = []
    adv_tir = []

    print("Bateaux du joueur :")
    for i in range(0, config["lines"] * config["columns"]):
        j_ships.append(int(objects[i].our_ship))
    for i in range(0, config["lines"] * config["columns"], config["columns"]):
        print(j_ships[i:i + config["columns"]])

    print("Tirs de l'adversaire :")
    for i in range(0, config["lines"] * config["columns"]):
        adv_tir.append(int(objects[i].adv_tir))
    for i in range(0, config["lines"] * config["columns"], config["columns"]):
        print(adv_tir[i:i + config["columns"]])


def affichage_our_tir(objects, config):
    """ Affichage de là ou a tiré le joueur
    :: config : fichier de configuration
    :: objects : plateau
    """

    j_fire = []
    for i in range(0, config["lines"] * config["columns"]):
        j_fire.append(int(objects[i].our_tir))
    for i in range(0, config["lines"] * config["columns"], config["columns"]):
        print(j_fire[i:i + config["columns"]])


def user_input_rules(configships, table):
    """ Règles d'entrées des inputs
    :: config : fichier de configuration
    :: table : tableau des coordonnées
    """

    while True:
        try:
            taille = int(input(
                "Entrer la taille de votre bateau (1-{}): ".format(len(configships.keys()) + 1)))
            if not taille in sorted([i for i in configships.keys()]):
                raise ValueError("Entrer un entier compris entre 1 et {}.".format(
                    len(configships.keys()) + 1))
            elif configships[taille] == 0:
                raise ValueError(
                    "Vous n'avez plus de bateau de taille {}.".format(taille))
            break
        except ValueError as VE:
            print(VE)

    while True:
        try:
            place = input("Entrer la première case de votre bateau : ")
            if not place in table:
                raise ValueError(
                    "Entrer une case qui est présente sur le plateau.")
            break
        except ValueError as VE:
            print(VE)

    while True:
        try:
            direction = input(
                "Entrer la direction vers laquelle se dirige votre navire (N/S/E/O) : ")
            if not direction in ['N', 'S', 'E', 'O']:
                raise ValueError("Entrer une direction valide.")
            break
        except ValueError as VE:
            print(VE)

    return taille, place, direction, configships


def alea_input_rules(configships, table, taille_list):
    """ Aléatoire
    :: configships : fichier de configuration
    :: table : tableau des coordonnées
    :: taille_list : listes des tailles possibles
    """

    while True:
        try:
            taille = random.choice(taille_list)
            if configships[taille] == 0:
                taille_list.remove(taille)
                raise ValueError
            break
        except ValueError as VE:
            pass

    place = random.choice(table)
    direction = random.choice(['N', 'S', 'E', 'O'])

    #print(taille, place, direction)

    return taille, place, direction, configships, taille_list


def ships_rules(config):
    """ Vérifie que le nombre total de bateaux n'est pas trop élevé
    :: config : fichier de configuration
    """

    # Tableau des nb de colones/lignes possibles
    liste_coord = [i for i in range(10, 27)]
    # Multiplication croisée, remove duplicates, tri par ordre croissant.
    prod_liste_coord = sorted(
        list(set([i * j for i in liste_coord for j in liste_coord])))
    # print(prod_liste_coord)

    # Affichage 0 si c'est une puissance entière
    sqrt_prod_liste_coord = [(math.sqrt(i) % 2) for i in prod_liste_coord]

    # Trouve l'emplacement des 0
    indices = [i for i, x in enumerate(sqrt_prod_liste_coord) if x == 0]
    # print(indices)

    nb_tot_cases = config["lines"] * config["columns"]  # Nombre de cases total

    nb_ships_allowed = 5  # Nombre de bateaux minimum
    for i in indices:
        if prod_liste_coord.index(nb_tot_cases) >= i:
            # print(i)
            nb_ships_allowed += 1
    nb_ships_allowed -= 1
    # print(nb_ships_allowed)

    return nb_ships_allowed


def main():
    """ Routine globale """

    print("Bataille Navale\n")

    # Configuration d'une partie par l'utilisateur ou utilisation d'une
    # configuration existante
    print("Choix de la configuration :")
    while True:
        try:
            conf = int(
                input("1. Créer un nouveau fichier,\n2. Utiliser un fichier existant,\n> "))
            if not conf in [1, 2]:
                raise ValueError("Entrer 1 ou 2.")
            break
        except ValueError as VE:
            print(VE)

    if conf == 1:
        print("Veuillez remplir le fichier de configuration de la partie à laquelle vous allez jouer.")
        # Fichier de configuration commun aux deux joueurs
        nb_tot_ships = configuration()
        # print(nb_tot_ships)
    elif conf == 2:
        config_list = read_config()
        while True:
            try:
                while True:
                    try:
                        num_conf = int(input(
                            "\nEntrer le nombre correspondant à la ligne de la configuration que vous voulez entrer :\n> "))
                        if not num_conf in range(1, len(config_list) + 1):
                            raise ValueError(
                                "Entrer un nombre compris entre 1 et {}.".format(len(config_list)))
                        break
                    except ValueError as VE:
                        print(VE)

                # Liste de tuples contenant la configuration choisie
                config_sorted = config_list[num_conf - 1]

                # Tests pour vérifier que la configuration est valide
                # (colonnes/lignes)
                if config_sorted[0][1] > 26 or config_sorted[0][1] < 10:
                    raise ValueError(
                        "Configuration choisie invalide. \nLe nombre de colonnes doit être un entier compris entre 10 et 26. \nModifier le fichier de configuration correspondant.")
                else:
                    config["columns"] = config_sorted[0][1]
                if config_sorted[1][1] > 26 or config_sorted[1][1] < 10:
                    raise ValueError(
                        "Configuration choisie invalide. \nLe nombre de lignes doit être un entier compris entre 10 et 26. \nModifier le fichier de configuration correspondant.")
                else:
                    config["lines"] = config_sorted[1][1]

                # Test d'un nombre de bateaux valide
                nb_tot_ships = sum([i for i in config_sorted[2][1].values()])
                # print(nb_tot_ships)
                nb_ships_allowed = ships_rules(config)
                if nb_tot_ships > nb_ships_allowed:
                    raise ValueError(
                        "Configuration choisie invalide. \nVous avez un nombre total de bateaux trop élevé par rapport à la taille du plateau. \nModifier le fichier de configuration correspondant.")

                # Vérification qu'il n'y a pas nb_ships_taille_sup >
                # nb_ships_taille_inf.
                for i in range(3):
                    if config_sorted[2][1][i + 2] < config_sorted[2][1][i + 3]:
                        raise ValueError(
                            "Configuration choisie invalide. \nVous avez plus de bateaux de taille {} que de bateaux de taille {}. \nModifier le fichier de configuration correspondant.".format(i + 3, i + 2))
                        break
                config["ships"] = config_sorted[2][1]
                break
            except ValueError as VE:
                print(VE)
        print("\nContenu du fichier de configuration choisi :\n", config)

    # Mode de jeu 2 joueurs ou contre l'IA
    print("\nChoix du mode jeux (PVP, PVE):")
    while True:
        try:
            mode = int(
                input("1. Joueur contre joueur,\n2. Joueur contre IA,\n> "))
            if not mode in [1, 2]:
                raise ValueError("Entrer 1 ou 2.")
            break
        except ValueError as VE:
            print(VE)

    # Classe représentant le premier joueur
    joueur1 = Player()
    while True:
        try:
            j1_nom = input(
                "Enter le nom du joueur 1 (20 caractères maximum):\n> ")
            if len(j1_nom) > 20:
                raise ValueError("Entrer un nom plus court.")
            break
        except ValueError as VE:
            print(VE)
    joueur1.name = j1_nom
    joueur1.ships_left = nb_tot_ships
    # print(joueur1)

    print("\nChoix du mode de génération de l'emplacement des bateaux pour {joueur1}:".format(
        joueur1=joueur1.name))
    while True:
        try:
            gen_j1 = int(
                input("1. Génération par le joueur,\n2. Génération aléatoire,\n> "))
            if not gen_j1 in [1, 2]:
                raise ValueError("Entrer 1 ou 2.")
            break
        except ValueError as VE:
            print(VE)

    table = plateau(objectsj1, config)

    if gen_j1 == 1:
        # Génération du plateau du joueur 1 par le joueur 1
        placement_joueur(objectsj1, nb_tot_ships, config, table)
    elif gen_j1 == 2:
        # Génération du plateau du joueur 1 aléatoirement
        while True:
            try:
                cote = int(
                    input("1. Autoriser les bateaux côtes à côtes,\n2. Ne pas autoriser les bateaux côtes à côtes,\n> "))
                if not cote in [1, 2]:
                    raise ValueError("Entrer 1 ou 2.")
                break
            except ValueError as VE:
                print(VE)
        if cote == 1:
            placement_joueur(objectsj1, nb_tot_ships,
                             config, table, aléatoire=True)
        elif cote == 2:
            placement_joueur(objectsj1, nb_tot_ships, config,
                             table, aléatoire=True, near=False)

    affichage_our_ships(objectsj1, config)
    joueur1.plateau = [i.__dict__ for i in objectsj1]
    print(joueur1)

    if mode == 1:
        # Classe représentant le second joueur
        joueur2 = Player()
        while True:
            try:
                j2_nom = input(
                    "Enter le nom du joueur 2 (20 caractères maximum):\n> ")
                if len(j2_nom) > 20:
                    raise ValueError("Entrer un nom plus court.")
                break
            except ValueError as VE:
                print(VE)
        joueur2.name = j2_nom
        joueur2.ships_left = nb_tot_ships
        # print(joueur2)

        print(
            "\nChoix du mode de génération de l'emplacement des bateaux pour le {joueur2}:".format(joueur2=joueur2.name))
        while True:
            try:
                gen_j2 = int(
                    input("1. Génération par le joueur,\n2. Génération aléatoire,\n> "))
                if not gen_j2 in [1, 2]:
                    raise ValueError("Entrer 1 ou 2.")
                break
            except ValueError as VE:
                print(VE)

        table = plateau(objectsj2, config)

        if gen_j2 == 1:
            # Génération du plateau du joueur 2 par le joueur 2
            placement_joueur(objectsj2, nb_tot_ships, config, table)
        elif gen_j2 == 2:
            # Génération du plateau du joueur 2 aléatoirement
            while True:
                try:
                    cote = int(
                        input("1. Autoriser les bateaux côtes à côtes,\n2. Ne pas autoriser les bateaux côtes à côtes,\n> "))
                    if not cote in [1, 2]:
                        raise ValueError("Entrer 1 ou 2.")
                    break
                except ValueError as VE:
                    print(VE)
            if cote == 1:
                placement_joueur(objectsj2, nb_tot_ships,
                                 config, table, aléatoire=True)
            elif cote == 2:
                placement_joueur(objectsj2, nb_tot_ships, config,
                                 table, aléatoire=True, near=False)

        affichage_our_ships(objectsj2, config)
        joueur2.plateau = [i.__dict__ for i in objectsj2]
        print(joueur2)
        joueur1, joueur2 = choose_starter(joueur1, joueur2)
        play(joueur1, joueur2, table)

    elif mode == 2:
        # Classe représentant l'IA
        joueur2 = Player()
        while True:
            try:
                joueur2_nom = input(
                    "Enter le nom de l'IA (20 caractères maximum):\n> ")
                if len(joueur2_nom) > 20:
                    raise ValueError("Entrer un nom plus court.")
                break
            except ValueError as VE:
                print(VE)
        joueur2.name = joueur2_nom
        joueur2.ships_left = nb_tot_ships

        # Génération aléatoire
        table = plateau(objectsj2, config)
        placement_joueur(objectsj2, nb_tot_ships,
                         config, table, aléatoire=True)
        affichage_our_ships(objectsj2, config)
        joueur2.plateau = [i.__dict__ for i in objectsj2]
        print(joueur2)
        joueur1, joueur2 = choose_starter(joueur1, joueur2)
        play(joueur1, joueur2, table, aléatoire=True)


if __name__ == '__main__':
    sys.exit(main())


# Variante "salvo": autant de tirs que de bateaux fonctionnels
# Variante : sans donner la position des cases touchées
# Timer sur la partie
# Touché / Touché coulé / OPTION : Touché avec annonce du navire
# Passage en jeu aléatoire pendant la partie

# Placement aléatoire sans toucher les bords (1 max ou au choix)

# Choix configuration plateau - position des navires prédéfinie pour être moins touché
# -- Espacer les navires d'une case OU les grouper dans un coin
