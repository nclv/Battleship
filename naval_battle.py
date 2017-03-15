#! python3.5
# -*- coding: utf-8 -*-

""" Bataille navale """

# Auteur : Nicolas Vincent T°S5
# 2017

import sys
import ast # eval()
import math
import itertools
import secrets # Nombres random
import string

class Configuration(object):
    """Classe de configuration du plateau.

    Attributes:
        config (dict): Fichier de configuration.
        file_name (str): Nom du fichier contenant la configuration avec extension '.txt'.
        nb_tot_ships (int): Nombre total de bateaux.
        mode (int): Mode de jeu.
        difficulte_IA (int): Difficulté de l'IA.
    """

    def __init__(self):
        """Initialisation de la classe.
        """

        self.difficulte_IA = None
        self.choose_file()
        self.choose_gamemode()
        self.choose_config()

    def new_configuration(self):
        """Cré une configuration contenant la taille du plateau, le nombre de bateaux et
        leur taille.

         - Test des différentes entrées 'columns' et 'lines' comprises entre 10 et 26.
         - Test d'entrée du nombre de bateaux et de leur taille en respectant 'ships_rules(config)'.
         - Tri de 'config' et écriture dans 'file_name' s'il n'y est pas déjà.

        Returns:
            nb_tot_ships (int): Nombre total de bateaux.
            config (dict): Fichier de configuration.

        Raises:
            ValueError: Erreurs des inputs.

        .. seealso:: ships_rules(), read_config(), confirm_input(), map().
        """

        # Tests des inputs du nb_lines,nb_columns, nb_bateaux
        while True:
            try:
                columns = int(input('Entrer le nombre de colones (10-26): '))
                if columns > 26 or columns < 10:
                    raise ValueError("Le nombre de colonnes doit être un entier compris entre 10 et 26.")
                break
            except ValueError as VE:
                print(VE)

        self.config["columns"] = columns

        while True:
            try:
                lines = int(input('Entrer le nombre de lignes (10-26): '))
                if lines > 26 or lines < 10:
                    raise ValueError("Le nombre de lignes doit être un entier compris entre 10 et 26.")
                break
            except ValueError as VE:
                print(VE)

        self.config["lines"] = lines

        while True:
            try:
                ships_values = list(map(int, input(
                    'Entrer à la suite les nombres de bateaux de tailles 2,3,4 et 5 séparés par une virgule : ').split(',')))
                # print(ships_values)

                # Test de l'input
                if len(ships_values) != 4:
                    raise ValueError("Entrer 4 valeurs séparées par des virgules.")
                # Validation de l'input
                if not self.confirm_input():
                    continue

                # Test d'un nombre de bateaux valide
                self.nb_tot_ships = sum([i for i in ships_values])
                # print(nb_tot_ships)
                nb_ships_allowed = self.ships_rules()
                if self.nb_tot_ships > nb_ships_allowed:
                    raise ValueError(
                        "Vous avez entré un nombre total de bateaux trop élevé par rapport à la taille du plateau.")

                # Vérification qu'il n'y a pas nb_ships_taille_sup >
                # nb_ships_taille_inf.
                for x, y in zip(ships_values, ships_values[1:]):
                    #print(x, y)
                    if x < y:
                        raise ValueError(
                            "Vous avez plus de bateaux de taille {} que de bateaux de taille {}.".format(y, x))
                break
            except ValueError as VE:
                print(VE)

        ships = {5: ships_values[3], 4: ships_values[2], 3: ships_values[
            1], 2: ships_values[0]}  # taille : nombre

        self.config["ships"] = ships

        # On trie le dictionnaire de configuration
        config_sorted = sorted(self.config.items(), key=lambda t: t[0])
        # Lit le fichier de configuration
        config_list = self.read_config()

        if not config_sorted in config_list:  # Si la config n'est pas déjà présente, on l'écrit
            with open(self.file_name, 'a') as f:
                f.write(str(config_sorted) + '\n')

        # Afficher config
        print("Contenu du fichier de configuration généré : ")
        for keys, values in self.config.items():
            print(keys, ':', values)

    def choose_file(self):
        """Choix d'un fichier contenant déjà des configurations.

        Returns:
            file_name (str): Nom du fichier.

        .. seealso:: confirm_input(), isalnum().
        """

        while True:
            try:
                self.file_name = input("Entrer le nom du fichier de configuration(lettres/chiffres), en cas de mauvaise entrée le fichier 'configs' est défini par défaut.\n> ")
                if not self.file_name.isalnum():
                    self.file_name = 'configs'
                if not self.confirm_input():
                    continue
                break
            except ValueError as VE:
                print(VE)

    def choose_config(self):
        """Configuration d'une partie par l'utilisateur ou utilisation d'une configuration existante.

        .. seealso:: new_configuration(), read_config().
        """

        print("Choix de la configuration :")
        while True:
            try:
                conf = int(
                    input("1. Créer une nouvelle configuration,\n2. Utiliser une configuration existante,\n> "))
                if not conf in [1, 2]:
                    raise ValueError("Entrer 1 ou 2.")
                break
            except ValueError as VE:
                print(VE)

        self.config = dict()

        if conf == 1:
            print("Veuillez remplir les paramètres de la configuration de la partie à laquelle vous allez jouer.")
            # Fichier de configuration commun aux deux joueurs
            self.new_configuration()
        elif conf == 2:
            config_list = self.read_config()
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
                        self.config["columns"] = config_sorted[0][1]
                    if config_sorted[1][1] > 26 or config_sorted[1][1] < 10:
                        raise ValueError(
                            "Configuration choisie invalide. \nLe nombre de lignes doit être un entier compris entre 10 et 26. \nModifier le fichier de configuration correspondant.")
                    else:
                        self.config["lines"] = config_sorted[1][1]

                    # Test d'un nombre de bateaux valide
                    self.nb_tot_ships = sum([i for i in config_sorted[2][1].values()])
                    # print(nb_tot_ships)
                    nb_ships_allowed = self.ships_rules()

                    if self.nb_tot_ships > nb_ships_allowed:
                        raise ValueError(
                            "Configuration choisie invalide. \nVous avez un nombre total de bateaux trop élevé par rapport à la taille du plateau. \nModifier le fichier de configuration correspondant.")

                    # Vérification qu'il n'y a pas nb_ships_taille_sup >
                    # nb_ships_taille_inf.
                    for i in range(3):
                        if config_sorted[2][1][i + 2] < config_sorted[2][1][i + 3]:
                            raise ValueError(
                                "Configuration choisie invalide. \nVous avez plus de bateaux de taille {} que de bateaux de taille {}. \nModifier le fichier de configuration correspondant.".format(i + 3, i + 2))
                            break
                    self.config["ships"] = config_sorted[2][1]
                    break
                except ValueError as VE:
                    print(VE)
            print("\nContenu du fichier de configuration choisi : \n",self.config, "\n")

    def choose_gamemode(self):
        """Choix du mode de jeu PVP ou PVE.

        Returns:
            self.mode: Mode de jeu.
        """

        # Mode de jeu 2 joueurs ou contre l'IA
        print("\nChoix du mode jeux (PVP, PVE):")
        while True:
            try:
                self.mode = int(
                    input("1. Joueur contre joueur,\n2. Joueur contre IA,\n> "))
                if not self.mode in [1, 2]:
                    raise ValueError("Entrer 1 ou 2.")
                break
            except ValueError as VE:
                print(VE)

    def read_config(self):
        """Lit le fichier de configuration config.txt situé dans le même dossier ou le cré.

        Extrait la liste des configurations.
        Affiche les configurations que l'utilisateur peut choisir.

        Returns:
            config_list_sorted (list): Configurations du fichier triées.
            self.file_name (str): Nom du fichier contenant la configuration avec extension '.txt'.

        .. seealso:: ast.literal_eval(), splitlines(), enumerate().
        """

        self.file_name += ".txt" # Ajout de l'extension .txt

        try:
            with open(self.file_name, 'r') as f:
                print("\nFichier contenant la configuration :", f.name)
                data = f.read()
        except IOError:
            f = open(self.file_name, "w")
            f.close()

        config_list = [ast.literal_eval(line) for line in data.splitlines()] # Liste des configurations
        config_list_sorted = [sorted(config_list[i]) for i, j in enumerate(config_list)] # Tri de la configuration

        # Affichage des configurations
        print("Configurations présentes dans le fichier.")
        for i in config_list_sorted:
            print(i)

        #print(config_list) # Liste de tuples
        return config_list_sorted

    def ships_rules(self):
        """ Vérifie que le nombre total de bateaux n'est pas trop élevé.

        Returns:
            nb_ships_allowed (int): Nombre de bateaux autorisés.

        .. seealso:: math.sqrt().

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

        nb_tot_cases = self.config["lines"] * self.config["columns"]  # Nombre de cases total

        nb_ships_allowed = 5  # Nombre de bateaux minimum (10*10)
        for i in indices:
            if prod_liste_coord.index(nb_tot_cases) >= i:
                # print(i)
                nb_ships_allowed += 1
        nb_ships_allowed -= 1
        # print(nb_ships_allowed)

        return nb_ships_allowed

    @classmethod
    def confirm_input(cls):
        """Demande de confirmer l'entrée.
        """

        verif = input("Valider la sélection (O/N): ")
        if not verif in ["O", "N"]:
            raise ValueError("Entrer 0 ou N.")
        if verif == "N":
            return False
        else:
            return True

    def __str__(self):
        """Affichage de tous les attributs de la classe.

        Returns:
            config (dict): Fichier de configuration.
            file_name (str): Nom du fichier contenant la configuration avec extension '.txt'.
            nb_tot_ships (int): Nombre total de bateaux.
            mode (int): Mode de jeu.
        """

        return "Configuration choisi : {},\nFichier contenant la configuration : {},\nNombre total de bateaux : {},\nMode de jeu : {},\nDifficulté de l'IA : {}\n".format(
            self.config, self.file_name, self.nb_tot_ships, self.mode, self.difficulte_IA)

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, name):
        """Est appelée quand on demande un attribut appelé "name" et qu'il n'existe pas."""

        return None

    def __delattr__(self, nom_attr):
        """On ne peut supprimer d'attribut, on lève l'exception AttributeError.

        Raises:
            AttributeError: Erreurs d'attribut.

        """

        raise AttributeError(
            "Vous ne pouvez supprimer aucun attribut de cette classe")


class Case(object):
    """Classe repésentant une case du plateau.

    Attributes:
        coordonnées (str): Coordonnée de la case.
        our_tir (boolean): Si nous avons effectué un tir sur cette position.
        adv_tir (boolean): Si l'adversaire a effectué un tir sur cette position.
        our_ship (int): Si un de nos bateaux est placé ici, prends la valeur de sa taille.
        adv_ship (boolean): Si un bateau adverse se trouve à cet emplacement.

    """

    def __init__(self):
        self.coordonnees = 0
        self.our_tir = False
        self.adv_tir = False
        self.our_ship = 0
        self.adv_ship = False

    def __str__(self):
        """Affichage de tous les attributs de la classe.

        Returns:
            coordonnées (str): Coordonnée de la case.
            our_tir (boolean): Si nous avons effectué un tir sur cette position.
            adv_tir (boolean): Si l'adversaire a effectué un tir sur cette position.
            our_ship (int): Si un de nos bateaux est placé ici, prends la valeur de sa taille.
            adv_ship (boolean): Si un bateau adverse se trouve à cet emplacement.

        """

        return "\nCoordonnées : {}, Tir effectué : {}, Tir reçu : {}, Bateau présent : {}, Bateau de l'adversaire : {}".format(
            self.coordonnees, self.our_tir, self.adv_tir, self.our_ship, self.adv_ship)

    def __repr__(self):
        return self.__str__()

    def __getattr__(self, name):
        """Est appelée quand on demande un attribut appelé "name" et qu'il n'existe pas."""

        return None

    def __delattr__(self, nom_attr):
        """On ne peut supprimer d'attribut, on lève l'exception AttributeError.

        Raises:
            AttributeError: Erreurs d'attribut.

        """

        raise AttributeError(
            "Vous ne pouvez supprimer aucun attribut de cette classe")


class Plateau(object):
    """Classe repésentant un plateau.

    Attributes:
        list_cases (list): Liste des objets Case().
        table (list): Coordonnées de toutes les cases du plateau.
    """

    table = []

    def __init__(self, config):
        """Initialisation du plateau.

        Args:
            config (dict): Fichier de configuration.

        .. seealso:: gen_coordonnees(), Case().
        """

        Plateau.table = self.gen_coordonnees(config)

        # Affichage des coordonnées
        #for i in range(0, config["lines"] * config["columns"], config["columns"]):
        #   print(table[i:i + config["columns"]])

        self.list_cases = []
        # Affichage des objets
        for i in range(config["lines"] * config["columns"]):
            self.list_cases.append('Case' + str(i))
            self.list_cases[i] = Case()
            self.list_cases[i].coordonnees = Plateau.table[i]

    def placement_boat(self, joueur, nb_tot_ships, config, table, near=True):
        """Emplacement des bateaux aléatoire ou choisi par le joueur.

        Args:
            nb_tot_ships (int): Nombre total de bateaux.
            config (dict): Fichier de configuration.
            table (list): Coordonnées de toutes les cases du plateau.
            joueur.aleatoire (boolean): Si le placement est aléatoire (IA) ou non (player).
            near (boolean): Si on autorise les bateaux côtes à côtes.

        .. seealso:: alea_input_rules(), user_input_rules(), near_cases_boat(), placement_boat_sub().

        """

        # Nombre de bateaux restant
        restant = sum([i for i in config["ships"].values()])
        # Variable modifiable sans interférer avec config
        configships = config["ships"].copy()

        # Liste des tailles disponibles
        taille_list = []
        for i in configships.keys():
            while taille_list.count(i) != configships[i]:
                taille_list.append(i)

        for _ in range(nb_tot_ships):
            restart = True
            while restart:  # Boucle infini pour répéter lorsqu'il y a une mauvaise entrée ou un bateau déjà présent
                restart = False
                placed = False  # Variable True si un bateau complet à été placé
                if joueur.aleatoire == True:
                    taille, place, direction, configships, taille_list = self.alea_input_rules(configships, table, taille_list)
                else:
                    taille, place, direction, configships = self.user_input_rules(configships, table)
                for i, value in enumerate(self.list_cases):  # Parcours de la liste d'objets
                    coordonnees = value.coordonnees
                    if coordonnees == place:  # Si on arrive aux coordonnées entrées
                        deplacement = self.test_directions(config, taille, direction, i)
                        # Liste des cases autour du bateau (test présence bateau)
                        test_cases_autour_boat = self.near_cases_boat(config, taille, deplacement, i)
                        if near == False and test_cases_autour_boat:
                            placed = False
                            restart = True
                            break
                        restart, placed = self.placement_boat_sub(joueur, config, taille, deplacement, i, restart, placed)
                        if placed:
                            # On décrémente de 1 le nb de bateaux de cette
                            # taille
                            configships[taille] -= 1
                            restant -= 1
                            if not joueur.aleatoire:
                                print("Votre bateau est bien placé.")
                                print("Il vous reste {} bateaux de taille {}.".format(
                                    configships[taille], taille))
                                print(
                                    "Il vous reste {} bateaux à placer.".format(restant))

    def placement_boat_sub(self, joueur, config, taille,
                             deplacement, i, restart, placed):
        """Placement, avec prise en compte de la direction, si les conditions sont vérifiées.

        Args:
            self.list_cases (class): Objet représentant une case.
            self.aleatoire (boolean): Si le placement est aléatoire (IA) ou non (player).
            config (dict): Fichier de configuration.
            taille (int): Taille du bateau.
            deplacement (tuple): Déplacement d'une unité réalisé en fonction de la direction choisie et valeur booléenne décrivant si l'on sort ou non du plateau.
            i (int): Emplacement initial du bateau.
            restart (boolean): Si l'on recommence la boucle en cas de mauvais placement.
            placed (boolean): Si le bateau complet est posé.

        Returns:
            restart (boolean): Si l'on recommence la boucle en cas de mauvais placement.
            placed (boolean): Si le bateau complet est posé.
            list_cases (class): Objet représentant une case.

        .. seealso:: Case(object), test_directions().

        """

        for j in range(taille):
            # Si on sort du plateau
            if deplacement[1]:
                if not joueur.aleatoire:
                    print("Votre bateau sort du plateau.")
                restart = True
                break
            elif self.list_cases[i + deplacement[0] * j].our_ship != 0:
                if not joueur.aleatoire:
                    print("Un bateau se trouve déjà à cet emplacement.")
                while j != 0:
                    j -= 1
                    self.list_cases[i + deplacement[0] * j].our_ship = 0
                placed = False
                restart = True
                break
            # On place le bateau
            self.list_cases[i + deplacement[0] * j].our_ship = taille
            placed = True

        return restart, placed

    def test_directions(self, config, taille, direction, i):
        """Test de si le bateau se trouve hors plateau.

        Args:
            list_cases (class): Objet représentant une case.
            config (dict): Fichier de configuration.
            taille (int): Taille du bateau.
            direction (str): Direction du bateau.
            i (int): Emplacement initial du bateau.

        Returns:
            deplacement (list): Déplacement d'une unité réalisé en fonction de la direction choisie et valeur booléenne décrivant si l'on sort ou non du plateau.

        .. seealso:: Case().

        """

        # Tests de si on sort du plateau
        if direction == 'N':
            emplacement_extrem = self.list_cases[(i - config["columns"] * (taille - 1)) % (config["columns"] * config["lines"])].coordonnees > self.list_cases[i].coordonnees
        elif direction == 'S':
            emplacement_extrem = self.list_cases[(i + config["columns"] * (taille - 1)) % (config["columns"] * config["lines"])].coordonnees < self.list_cases[i].coordonnees
        elif direction == 'E':
            emplacement_extrem = self.list_cases[(i + taille - 1) % (config["columns"] * config["lines"])].coordonnees[0] != self.list_cases[i].coordonnees[0]
        elif direction == 'O':
            emplacement_extrem = self.list_cases[(i - (taille - 1)) % (config["columns"] * config["lines"])].coordonnees[0] != self.list_cases[i].coordonnees[0]

        all_deplacement = {'N': [-config["columns"]], 'S': [config["columns"]], 'E': [1], 'O': [-1]}

        # Création de la liste correspondant à la direction
        all_deplacement[direction].append(emplacement_extrem)
        deplacement = all_deplacement[direction]

        return deplacement

    def near_cases_boat(self, config, taille, deplacement, i):
        """Retourne une liste de la présence de bateaux sur les cases adjacentes d'un bateau en prennant en compte le bateau lui-même.

        Args:
            config (dict): Fichier de configuration.
            taille (int): Taille du bateau.
            deplacement (tuple): Déplacement d'une unité réalisé en fonction de la direction choisie et valeur booléenne décrivant si l'on sort ou non du plateau.
            i (int): Emplacement initial du bateau.

        Returns:
            cases_autour_boat (list): Liste des cases autour du bateau en prennant en compte le bateau.

        .. seealso:: near_cases(), test_directions().
        """

        cases_autour_boat = []

        for j in range(taille + 2):
            cases_autour_boat.extend(self.near_cases(config, i + deplacement[0] * j))

        test_cases_autour_boat = len(cases_autour_boat) != cases_autour_boat.count(0) + cases_autour_boat.count(taille) or cases_autour_boat.count(taille) > taille
        # print(cases_autour_boat)
        return test_cases_autour_boat

    def near_cases(self, config, place):
        """ Regarde s'il y a des bateaux sur les cases adjacentes d'une case

        Args:
            config (dict): Fichier de configuration.
            place (int): Emplacement de la case bateau.

        Returns:
            cases_autour (list): Liste des cases autour d'une case bateau.

        Raises:
            IndexError: Emplacement qui n'est pas présent dans le tableau.
        """

        cases_autour = []

        for i in [- config["columns"], config["columns"], - 1, 1]:
            try:
                cases_autour.append(self.list_cases[place + i].our_ship)
            except IndexError:
                cases_autour.append(0)

        # print(cases_autour)
        return cases_autour

    def affichage_our_ships(self, config):
        """Affichage des bateaux du joueur et des attaques de l'adversaire.

        Args:
            config (dict): Fichier de configuration.
        """

        print("Bateaux du joueur :")
        j_ships = [int(self.list_cases[i].our_ship) for i in range(0, config["lines"] * config["columns"])]
        [print(j_ships[i:i + config["columns"]]) for i in range(0, config["lines"] * config["columns"], config["columns"])]
        print("Tirs de l'adversaire :")
        adv_tir = [int(self.list_cases[i].adv_tir) for i in range(0, config["lines"] * config["columns"])]
        [print(adv_tir[i:i + config["columns"]]) for i in range(0, config["lines"] * config["columns"], config["columns"])]

    def affichage_our_tir(self, config):
        """ Affichage de là ou a tiré le joueur.

        Args:
            config (dict): Fichier de configuration.
        """

        print("Tirs du joueur :")
        j_fire = [int(self.list_cases[i].our_tir) for i in range(0, config["lines"] * config["columns"])]
        [print(j_fire[i:i + config["columns"]]) for i in range(0, config["lines"] * config["columns"], config["columns"])]

    @staticmethod # Pas de self car ne dépend pas de l'instance créée et est valable pour toutes
    def gen_coordonnees(config):
        """Cré un plateau de jeu pouvant aller jusqu'à 26*26 cases.
        - Axe vertical : A - Z.
        - Axe horizontal : 0 - 26.

        Affichage du plateau généré

        Args:
            config (dict): Fichier de configuration.

        Returns:
            table (list): Coordonnées de toutes les cases du plateau.

        .. seealso:: itertools.product()

        """

        # Génération des coordonnées :
        # Lettres de l'alphabet en ordonnée selon le nb de lignes voulues
        ordonnes = list(string.ascii_uppercase[:config["lines"]])
        # En abscisse les chiffres correspondant
        abscisses = [str(i) for i in range(config["columns"])]
        # print(ordonnes,abscisses)

        # On transforme les couples lettre/chiffre en string
        table = ["".join(value) for value in list(itertools.product(ordonnes, abscisses))]

        return table

    @staticmethod
    def user_input_rules(configships, table):
        """ Règles d'entrées des inputs.

        Args:
            configships (dict): Copie des bateaux du fichier de configuration. Décrémentée du bateau placé.
            table (list): Coordonnées de toutes les cases du plateau.

        Returns:
            taille (int): Taille du bateau.
            place (str): Emplacement d'une de ses extrémités.
            direction (str): Direction du bateau.
            configships (dict): Copie des bateaux du fichier de configuration.

        Raises:
            ValueError: Erreurs des inputs.
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

    @staticmethod
    def alea_input_rules(configships, table, taille_list):
        """Choix aléatoire.

        Args:
            configships (dict): Copie des bateaux du fichier de configuration. Décrémentée du bateau placé.
            table (list): Coordonnées de toutes les cases du plateau.
            taille_list (list): Listes des tailles possibles.

        Returns:
            taille (int): Taille du bateau.
            place (str): Emplacement d'une de ses extrémités.
            direction (str): Direction du bateau.
            configships (dict): Copie des bateaux du fichier de configuration.
            taille_list (list): Liste des tailles disonibles.

        Raises:
            ValueError: Erreurs des inputs.
        """

        while True:
            try:
                taille = secrets.choice(taille_list)
                if configships[taille] == 0:
                    taille_list.remove(taille)
                    raise ValueError
                break
            except ValueError:
                pass

        place = secrets.choice(table)
        direction = secrets.choice(['N', 'S', 'E', 'O'])

        #print(taille, place, direction)

        return taille, place, direction, configships, taille_list

    def __str__(self):
        """Affichage de tous les attributs de la classe.

        Returns:
            list_cases (list): Liste des objets Case().
        """

        return "Liste des objets Case(): {}\n".format(self.list_cases)

    def __getattr__(self, name):
        """Est appelée quand on demande un attribut appelé "name" et qu'il n'existe pas."""

        return None

    def __delattr__(self, nom_attr):
        """On ne peut supprimer d'attribut, on lève l'exception AttributeError.

        Raises:
            AttributeError: Erreurs d'attribut.
        """

        raise AttributeError(
            "Vous ne pouvez supprimer aucun attribut de cette classe")


class Player(object):
    """Classe représentant un joueur.

    Attributes:
        name (str): Nom du joueur, passé sur 'IA' par défaut.
        plateau (list): Cases du plateau du joueur.
        start (boolean): A commencé où non la partie.
        tir (int): Nombre de tirs effectués.
        ships_left (int): Nombre de bateaux restant.
        ships_lose (int): Nombre de bateaux perdus.
        ships_hit (int): Nombre de cases bateaux touchées.
        aleatoire (boolean): Variable utile au placement.
    """

    def __init__(self, conf, plateau_joueur):
        """Constructeur de la classe.

        Args:
            conf (class instance): Configuration du jeu.
            plateau_joueur (class instance): Plateau du joueur.
        """

        self.name = None
        self.plateau = plateau_joueur
        self.start = False  # Commencé ou non la partie
        self.tir = 0  # Nb tirs effectués
        self.ships_left = 5  # 5 bateaux restant (bataille navale classique)
        self.ships_lose = 0  # 0 bateaux coulé
        self.ships_hit = 0  # 0 case bateau touché
        self.aleatoire = None

    def name_input(self, nb_tot_ships, j_type):
        """Demande le nom du joueur.

        Args:
            conf.nb_tot_ships (int): Nombre total de bateaux.
            j_type (str): IA ou Human.

        Returns:
            self.name : Nom du joueur.
            self.ships_left: Bateaux restants.

        Raises:
            ValueError: Erreurs des inputs.
        """

        while True:
            try:
                j1_nom = input(
                    "Enter le nom {joueur} (20 caractères maximum):\n> ".format(joueur=j_type))
                if len(j1_nom) > 20:
                    raise ValueError("Entrer un nom plus court.")
                break
            except ValueError as VE:
                print(VE)
        self.name = j1_nom
        self.ships_left = nb_tot_ships

    def __str__(self):
        """Affichage de tous les attributs de la classe.

        Returns:
            name (str): Nom du joueur, passé sur 'IA' par défaut.
            plateau (list): Cases du plateau du joueur.
            start (boolean): A commencé où non la partie.
            tir (int): Nombre de tirs effectués.
            ships_left (int): Nombre de bateaux restant.
            ships_lose (int): Nombre de bateaux perdus.
            ships_hit (int): Nombre de cases bateaux touchées.
            aleatoire (boolean): Variable utile au placement.
        """

        return "Nom : {},\nPlateau : {},\nA commencé la partie : {},\nNombre de tirs effectués : {},\nNombre de bateaux restant : {},\nNombre de bateaux coulés : {},\nNombre de cases bateau touchées : {},\nValeur du placement aléatoire : {}\n".format(
            self.name, self.plateau, self.start, self.tir, self.ships_left, self.ships_lose, self.ships_hit, self.aleatoire)

    def __getattr__(self, name):
        """Est appelée quand on demande un attribut appelé "name" et qu'il n'existe pas."""

        return None

    def __delattr__(self, nom_attr):
        """On ne peut supprimer d'attribut, on lève l'exception AttributeError.

        Raises:
            AttributeError: Erreurs d'attribut.
        """

        raise AttributeError(
            "Vous ne pouvez supprimer aucun attribut de cette classe")

class PlayerHuman(Player):
    """Classe représentant un joueur humain.

    Attributes:
        (Hérite des attributs de la classe Player().)
    """

    def __init__(self, conf, plateau_joueur):
        """Constructeur de la classe.
        On reprend le constructeur de Player().
        """

        super().__init__(conf, plateau_joueur)
        self.aleatoire = False
        self.gen_Human(conf.config, conf.nb_tot_ships, Plateau.table, plateau_joueur)

    def gen_Human(self, config, nb_tot_ships, table, plateau_joueur):
        """Génère le plateau et les attributs d'un joueur.

        Args:
            conf.config (dict): Fichier de configuration.
            conf.nb_tot_ships (int): Nombre total de bateaux.
            Plateau.table (list): Coordonnées de toutes les cases du plateau.
            plateau_joueur (list): Plateau du joueur.

        Returns:
            self.plateau: Plateau avec bateaux.

        .. seealso:: placement_boat(), affichage_our_ships(), name_input().
        """

        self.name_input(nb_tot_ships, 'du joueur')

        print("\nChoix du mode de génération de l'emplacement des bateaux pour {joueur1}:".format(
            joueur1=self.name))
        while True:
            try:
                gen_j1 = int(
                    input("1. Génération par le joueur,\n2. Génération aléatoire,\n> "))
                if not gen_j1 in [1, 2]:
                    raise ValueError("Entrer 1 ou 2.")
                break
            except ValueError as VE:
                print(VE)

        if gen_j1 == 1:
            # Génération du plateau du joueur 1 par le joueur 1
            plateau_joueur.placement_boat(self, nb_tot_ships, config, table)
        elif gen_j1 == 2:
            # On mets temporairement self.aleatoire à True
            self.aleatoire = True
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
                plateau_joueur.placement_boat(self, nb_tot_ships, config, table)
            elif cote == 2:
                plateau_joueur.placement_boat(self, nb_tot_ships, config, table, near=False)

            self.aleatoire = False

        plateau_joueur.affichage_our_ships(config)


class PlayerIA(Player):
    """Classe représentant un joueur IA.

    Attributes:
        (Hérite des attributs de la classe Player().)
    """

    def __init__(self, conf, plateau_joueur):
        """Constructeur de la classe.
        On reprend le constructeur de Player().
        """

        super().__init__(conf, plateau_joueur)
        self.aleatoire = True
        self.gen_IA(conf.config, conf.nb_tot_ships, Plateau.table, plateau_joueur)

    def gen_IA(self, config, nb_tot_ships, table, plateau_joueur):
        """Génère le plateau et les attributs d'un joueur.

        Args:
            conf.config (dict): Fichier de configuration.
            conf.nb_tot_ships (int): Nombre total de bateaux.
            Plateau.table (list): Coordonnées de toutes les cases du plateau.
            plateau_joueur (list): Plateau du joueur.

        Returns:
            self.plateau: Plateau avec bateaux.

        .. seealso:: placement_boat(), affichage_our_ships(), name_input().
        """

        self.name_input(nb_tot_ships, 'de l\'IA')

        plateau_joueur.placement_boat(self, nb_tot_ships, config, table)
        plateau_joueur.affichage_our_ships(config)


class strategie_IA(object):
    """Stratégie de l'IA en fonction de la difficulté en prennant en compte les coups précédents.

    Attributes:
        difficulte (int): Difficulté de l'IA.
        table_allowed (list): Coordonnées des cases qui ne sont pas encore jouées.
        possibilites (list): Liste des emplacements où il y a un bateau adverse (sans bateau complet).
        horizontal (boolean): Si le bateau est orienté Est/Ouest.
        vertical (boolean): Si le bateau est orienté Nord/Sud.
        directions (list): Copie de direct à laquelle on enlève les directions déjà choisies.
        direct (list): Toutes directions possibles.
    """

    def __init__(self, conf):
        """Constructeur de la classe.

        Initialisation des différents paramètres se retrouvant tour après tour.
        """

        self.choose_difficulte()
        conf.difficulte_IA = self.difficulte

        self.table_allowed = Plateau.table.copy()
        self.possibilites = set()  # Tableau des cases où se trouve un bateau adverse
        self.horizontal = False
        self.vertical = False
        self.direct = ['N', 'S', 'E', 'O']
        self.directions = self.direct.copy()

    def choose_difficulte(self):
        """Choix par l'utilisateur de la difficulté de l'IA.

        Args:
            self.difficulte (int): Difficulté de l'IA.

        Returns:
            self.difficulte (int): Difficulté de l'IA.
        """

        while True:
            try:
                diff = int(
                    input("Choisissez la difficulté de l'IA :\n 0. Très facile\n 1. Facile\n 2. Moyenne\n 3. Difficile\n> "))
                if not diff in range(4):
                    raise ValueError("Entrer une valeur comprise entre 0 et 3.")
                break
            except ValueError as VE:
                print(VE)

        self.difficulte = diff

    def exec_strategie(self, joueur1, joueur2, config):
        """Exécute la stratégie correspondant à la difficulté donnée à l'IA.

        Args:
            Attributs de la classe correspondant à la fonction appelée.
        """

        if self.difficulte == 0:
            position = self.strategie_alea()
        elif self.difficulte == 1:
            position = self.strategie_naive(joueur1, joueur2, config)
        elif self.difficulte == 2:
            position = self.strategie_naive_parite(joueur1, joueur2, config)

        return position

    def strategie_alea(self):
        """Stratégie complètement aléatoire.

        Args:
            self.table_allowed (list): Coordonnées des cases qui ne sont pas encore jouées.

        Returns:
            self.table_allowed (list): Coordonnées des cases qui ne sont pas encore jouées.
            self.position (str): Coordonnée de la case visée.
        """

        position = secrets.choice(self.table_allowed)
        self.table_allowed.remove(position)

        return position

    def strategie_naive(self, joueur1, joueur2, config):
        """Stratégie de jeu de l'IA: un bateau à la fois.

        Recherche de bateaux sur les cases adjacentes si case bateau touchée.
        Quand trouvé, continuer sur la même ligne.
        Quand il n'y en a plus, s'arrêter : passer de l'autre côté ou retourner aléatoire si bateau coulé.

        Args:
            joueur1 (class instance): Instance de la classe Player() du joueur 1.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.
            conf.config (dict): Fichier de configuration.
            self.table_allowed (list): Coordonnées des cases qui ne sont pas encore jouées.
            self.possibilites (set): Liste des emplacements où il y a un bateau adverse (sans bateau complet).
            self.horizontal (boolean): Si le bateau est orienté Est/Ouest.
            self.vertical (boolean): Si le bateau est orienté Nord/Sud.
            self.directions (list): Copie de direct à laquelle on enlève les directions déjà choisies.
            self.direct (list): Toutes directions possibles.

        Returns:
            joueur1 (class instance): Instance de la classe Player() du joueur 1.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.
            self.table_allowed (list): Coordonnées des cases qui ne sont pas encore jouées.
            position (str): Coordonnée de la case visée.
            self.horizontal (boolean): Si le bateau est orienté Est/Ouest.
            self.vertical (boolean): Si le bateau est orienté Nord/Sud.
            self.directions (list): Copie de direct à laquelle on enlève les directions déjà choisies.

        .. seealso:: zip(), test_directions().
        """

        restart = True
        while restart:  # Boucle infini pour répéter lsq'il y a une mauvaise entrée ou un bateau déjà présent
            restart = False

            print(self.possibilites)
            self.possibilites = list({i for i in range(len(joueur2.plateau.list_cases)) if joueur2.plateau.list_cases[i].adv_ship == True})
            print(self.possibilites)

            boat = [joueur1.plateau.list_cases[i].our_ship for i in range(len(joueur1.plateau.list_cases)) if i in self.possibilites]
            print(boat)

            # Test même valeur dans boat
            if boat and boat.count(boat[0]) == boat[0]:  # (2,2,3,3) : nb 2 = 2
                joueur1.ships_left -= 1
                joueur1.ships_lose += 1
                self.horizontal, self.vertical = False, False
                # All index of the first value
                for _ in [i for i, val in enumerate(boat) if val == boat[0]]:
                    # Emplacement dans possibilites des valeurs puis remplacement
                    # valeurs dans joueur2.plateau
                    joueur2.plateau.list_cases[self.possibilites[0]].adv_ship = boat[0]
                    self.possibilites.remove(self.possibilites[0])
                    self.directions = self.direct.copy()

            # Test deux cases bateau adjacentes
            self.possibilites.sort()
            for x, y in zip(self.possibilites, self.possibilites[1:]):
                #print(x, y)
                if x + 1 == y:
                    self.horizontal = True
                elif x + config["columns"] == y:
                    self.vertical = True
                else:
                    self.horizontal, self.vertical = False, False

            print(self.horizontal, self.vertical)

            if not self.possibilites:  # Test liste vide
                position = secrets.choice(self.table_allowed)
                print(position)
            elif len(self.possibilites) == 1:  # Test 1 seul élément
                direction = secrets.choice(self.directions)
            elif self.horizontal:  # Test 2 éléments côtes à côtes
                direction = secrets.choice(self.direct[2:])
            elif self.vertical:  # Test 2 éléments l'un en dessous de l'autre
                direction = secrets.choice(self.direct[:2])

            if self.possibilites:
                if (joueur2.plateau.list_cases[(self.possibilites[0] - 1) % (config["columns"] * config["lines"])].coordonnees not in self.table_allowed and self.horizontal) or (
                        joueur2.plateau.list_cases[(self.possibilites[0] - config["columns"]) % (config["columns"] * config["lines"])].coordonnees not in self.table_allowed and self.vertical):
                    case_bateau = self.possibilites[-1]
                elif (joueur2.plateau.list_cases[(self.possibilites[-1] + 1) % (config["columns"] * config["lines"])].coordonnees not in self.table_allowed and self.horizontal) or (joueur2.plateau.list_cases[(self.possibilites[-1] + config["columns"]) % (config["columns"] * config["lines"])].coordonnees not in self.table_allowed and self.vertical):
                    case_bateau = self.possibilites[0]
                else:
                    case_bateau = secrets.choice(
                        [self.possibilites[0], self.possibilites[-1]])
                print(case_bateau)
                if case_bateau == self.possibilites[0] and self.horizontal:
                    direction = self.direct[3]
                elif case_bateau == self.possibilites[0] and self.vertical:
                    direction = self.direct[0]
                elif case_bateau == self.possibilites[-1] and self.horizontal:
                    direction = self.direct[2]
                elif case_bateau == self.possibilites[-1] and self.vertical:
                    direction = self.direct[1]
                print(direction)
                # Si on ne sort pas du plateau
                if not joueur2.plateau.test_directions(config, 2, direction, case_bateau)[1]:
                    position = joueur2.plateau.list_cases[case_bateau + joueur2.plateau.test_directions(config, 2, direction, case_bateau)[0]].coordonnees
                    print(position)
                    if direction in self.directions:
                        self.directions.remove(direction)
                else:
                    restart = True
                    continue
                #print(self.directions)

            if position in self.table_allowed:
                # (34,35,36) si case_bateau = 34 et que direction = E, la position 35 n'est déjà plus dans table_allowed, on passe à l'autre case_bateau
                self.table_allowed.remove(position)
            else:
                restart = True
                continue
        #print(position)
        return position

    def strategie_naive_parite(self, joueur1, joueur2, config):
        """Stratégie de jeu de l'IA: un bateau à la fois avec amélioration parité.

        Recherche de bateaux sur les cases adjacentes si case bateau touchée.
        Quand trouvé, continuer sur la même ligne.
        Quand il n'y en a plus, s'arrêter : passer de l'autre côté ou retourner aléatoire si bateau coulé.

        Args:
            joueur1 (class instance): Instance de la classe Player() du joueur 1.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.
            conf.config (dict): Fichier de configuration.
            self.table_allowed (list): Coordonnées des cases qui ne sont pas encore jouées (cases paires)
            self.possibilites (set): Liste des emplacements où il y a un bateau adverse (sans bateau complet).
            self.horizontal (boolean): Si le bateau est orienté Est/Ouest.
            self.vertical (boolean): Si le bateau est orienté Nord/Sud.
            self.directions (list): Copie de direct à laquelle on enlève les directions déjà choisies.
            self.direct (list): Toutes directions possibles.

        Returns:
            joueur1 (class instance): Instance de la classe Player() du joueur 1.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.
            self.table_allowed (list): Coordonnées des cases qui ne sont pas encore jouées.
            position (str): Coordonnée de la case visée.
            self.horizontal (boolean): Si le bateau est orienté Est/Ouest.
            self.vertical (boolean): Si le bateau est orienté Nord/Sud.
            self.directions (list): Copie de direct à laquelle on enlève les directions déjà choisies.

        .. seealso:: zip(), test_directions().
        """

        self.table_allowed = self.table_allowed[::2]
        position = self.strategie_naive(joueur1, joueur2, config)

        return position

    def __str__(self):
        """Affichage de tous les attributs de la classe.

        Returns:
            self.difficulte (int): Difficulté de l'IA.
            self.table_allowed (list): Coordonnées des cases qui ne sont pas encore jouées.
            self.possibilites (list): Liste des emplacements où il y a un bateau adverse (sans bateau complet).
            self.horizontal (boolean): Si le bateau est orienté Est/Ouest.
            self.vertical (boolean): Si le bateau est orienté Nord/Sud.
            self.directions (list): Copie de direct à laquelle on enlève les directions déjà choisies.
            self.direct (list): Toutes directions possibles.
        """

        return "Difficulté : {},\nCoordonnées libres : {},\nCase contenant un bateau : {},\nOrientation horizontale : {},\nOrientation verticale : {},\nToutes les directions : {},\nDirections possibles : {},\n".format(self.difficulte, self.table_allowed, self.possibilites, self.horizontal, self.vertical, self.direct, self.directions)

    def __getattr__(self, name):
        """Est appelée quand on demande un attribut appelé "name" et qu'il n'existe pas."""

        return None

    def __delattr__(self, nom_attr):
        """On ne peut supprimer d'attribut, on lève l'exception AttributeError.

        Raises:
            AttributeError: Erreurs d'attribut.
        """

        raise AttributeError(
            "Vous ne pouvez supprimer aucun attribut de cette classe")


class Battleship(object):
    """Classe définissant le jeu en lui même.

    Attributes:
        joueur1 (class instance): Instance de la classe Player() du joueur 1.
        joueur2 (class instance): Instance de la classe Player() du joueur 2.
        conf (class instance): Instance de la classe Configuration().
    """

    def __init__(self):
        """Constructeur de la classe.
        """

        self.conf = Configuration()

        plateau_joueur1 = Plateau(self.conf.config)
        plateau_joueur2 = Plateau(self.conf.config)

        self.joueur1 = PlayerHuman(self.conf, plateau_joueur1)

        if self.conf.mode == 1:
            self.joueur2 = PlayerHuman(self.conf, plateau_joueur2)
        elif self.conf.mode == 2:
            self.joueur2 = PlayerIA(self.conf, plateau_joueur2)
            self.IA = strategie_IA(self.conf)

        self.choose_starter()
        self.play(self.conf.config, Plateau.table)


    def choose_starter(self):
        """Choix de qui commence.


        Args:
            self.joueur1 (class instance): Instance de la classe Player() du joueur 1.
            self.joueur2 (class instance): Instance de la classe Player() du joueur 2.

        Raises:
            ValueError: Erreurs des inputs.

        Returns:
            self.joueur1 (class instance): Instance de la classe Player() du joueur 1.
            self.joueur2 (class instance): Instance de la classe Player() du joueur 2.
        """

        while True:
            try:
                start = input(
                    "Choisissez qui commence la partie (1, 2, A): ")
                if not start in ['1', '2', 'A']:
                    raise ValueError("Entrer 1, 2 ou A.")
                if start == 'A':
                    start = secrets.choice(['1', '2'])
                break
            except ValueError as VE:
                print(VE)

        if start == '1':
            self.joueur1.start = True
            print("{joueur1} commence la partie.".format(joueur1=self.joueur1.name))
        elif start == '2':
            self.joueur2.start = True
            print("{joueur2} commence la partie.".format(joueur2=self.joueur2.name))

    def play(self, config, table):
        """Jeu tour par tour.

        Args:
            self.joueur1 (class instance): Instance de la classe Player() du joueur 1.
            self.joueur2 (class instance): Instance de la classe Player() du joueur 2.
            self.aleatoire (boolean): Si le placement est aléatoire (IA) ou non (player).
            table (list): Coordonnées de toutes les cases du plateau.

        Raises:
            ValueError: Erreurs des inputs.

        .. seealso:: strategie_naive().
        """

        # Mise en place du joueur qui commence la partie
        if self.joueur1.start == True:
            first = self.joueur1
            second = self.joueur2
        elif self.joueur2.start == True:
            first = self.joueur2
            second = self.joueur1

        altern_joueur = [first, second]

        # Boucle globale
        n = 0
        fin_partie = False
        while not fin_partie:
            while not fin_partie:
                try:
                    if self.joueur2.aleatoire == True and n % 2 == altern_joueur.index(self.joueur2):
                        position = self.IA.exec_strategie(self.joueur1, self.joueur2, self.conf.config)
                        print(self.IA)
                    else:
                        position = input("Entrer la case cible de votre tir : ")
                        if not position in table:
                            raise ValueError(
                                "Entrer une case qui est présente sur le plateau.")
                    for i in range(len(altern_joueur[n % 2].plateau.list_cases)):
                        if altern_joueur[n % 2].plateau.list_cases[i].coordonnees == position:
                            if altern_joueur[n % 2].plateau.list_cases[i].our_tir == False:
                                # 1 tir de plus effectué
                                altern_joueur[n % 2].tir += 1
                                # Emplacement sur lequel on a tiré
                                altern_joueur[n % 2].plateau.list_cases[i].our_tir = True
                                altern_joueur[(n + 1) %2].plateau.list_cases[i].adv_tir = True
                                # Test présence d'un bateau
                                if altern_joueur[(n + 1) %2].plateau.list_cases[i].our_ship != 0:
                                    altern_joueur[n % 2].ships_hit += 1
                                    altern_joueur[n % 2].plateau.list_cases[i].adv_ship = True
                            elif altern_joueur[n % 2].plateau.list_cases[i].our_tir == True:
                                raise ValueError("Vous avez déjà tiré sur cette position.")
                    #print(altern_joueur[n % 2])
                    altern_joueur[n % 2].plateau.affichage_our_ships(config)
                    altern_joueur[n % 2].plateau.affichage_our_tir(config)
                    if altern_joueur[n % 2].ships_left == 0:
                        fin_partie = True
                    break
                except ValueError as VE:
                    print(VE)

        # Test bateau coulé
        # Si aucune case bateau autour --> bateau coulé
        # While sur une même droite
        # Si mêmes chiffres avec adv_tir --> bateau coulé
        # Quand on connaît la taille du bateau attaqué, adv_ships = taille
            n += 1
        print("La partie est terminée.\n{gagnant} a gagné !!!".format(gagnant=altern_joueur[n % 2].name))

    def __str__(self):
        """Affichage de tous les attributs de la classe.

        Returns:
            self.joueur1 (class instance): Instance de la classe Player() du joueur 1.
            self.joueur2 (class instance): Instance de la classe Player() du joueur 2.
            self.conf (class instance): Instance de la classe Configuration().
        """

        return "Configuration : {},\nJoueur 1 : {},\nJoueur 2 : {}\n".format(self.conf, self.joueur1, self.joueur2)

    def __getattr__(self, name):
        """Est appelée quand on demande un attribut appelé "name" et qu'il n'existe pas."""

        return None

    def __delattr__(self, nom_attr):
        """On ne peut supprimer d'attribut, on lève l'exception AttributeError.

        Raises:
            AttributeError: Erreurs d'attribut.
        """

        raise AttributeError(
            "Vous ne pouvez supprimer aucun attribut de cette classe")


if __name__ == '__main__':
    sys.exit(Battleship())
