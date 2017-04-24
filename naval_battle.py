#! python3.6
# -*- coding: utf-8 -*-

"""naval_battle.py: Jeu de bataille navale. """

import sys
import os
import time
import argparse # Add command-line arguments support
import ast # eval()
import math
import itertools
import operator
import secrets # Nombres random
import string
import functools
import pandas # Affichage plateau
import numpy as np # Array


def timethis(func):
    """ Decorator that reports the execution time.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end-start)
        return result
    return wrapper

def while_true(func):
    """ Décore la fonction d'une boucle while True pour les inputs.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            try:
                res = func(*args, **kwargs)
                if res == 'verif':
                    continue
                break
            except ValueError as VE:
                print(VE)
        return res
    return wrapper
    
class Configuration(object):
    """Classe de configuration du plateau.

    Attributes:
        config (dict): Fichier de configuration.
        file_name (str): Nom du fichier contenant la configuration avec extension '.txt'.
        nb_tot_ships (int): Nombre total de bateaux.
        mode (int): Mode de jeu.
        difficulte_IA (int): Difficulté de l'IA.
    """

    def __init__(self, args, parser):
        """Initialisation de la classe.

        Args:
            args (class instance): Argument entrés en ligne de commande.
            parser (class instance): Parser de la ligne de commande.
        
        .. seealso:: verif_parser(), choose_gamemode(), choose_file(), choose_config()
        """

        self.file_name = args.file_name
        self.mode = args.mode
        self.config = dict()

        # Vérification des inputs création et choix de configuration
        self.verif_parser(args, parser)
        # Test des options sur le cmd
        if self.mode is None:
            self.choose_gamemode()
        if self.file_name is None:
            self.choose_file()
        if not self.file_name.endswith(".txt"): self.file_name += ".txt" # Ajout de l'extension .txt si elle n'y est pas déjà
        if not hasattr(args, 'columns') and args.exist_config is None:
            self.choose_config()

        self.difficulte_IA = None
        
    def verif_boat_input(self, func, boat_list, verif=False):
        """ Vérification que les inputs des bateaux sont corrects.
        
        Args:
            func (function): Fonction qui gère les erreurs.
            boat_list (list): Liste du nombre de bateaux entrée.
            verif (boolean): Confirmation de l'input.
            
        Returns:
            boat_list (list): Liste du nombre de bateaux entrée.
            
        Raises:
            func: Erreurs des inputs sur le cmd (parser.error) ou de l'utilisateur (ValueError).
        
        .. seealso:: confirm_input().
        """
        
        # Test de l'input
        if len(boat_list) != 4:
            raise func('Il existe seulement 4 types de bateaux différents et non {}.'.format(len(args.boat)))
        # Validation de l'input
        if verif and not self.confirm_input():
            return 'verif'
        
        # Test d'un nombre de bateaux valide
        self.nb_tot_ships = sum([i for i in boat_list])
        if self.nb_tot_ships > self.nb_ships_allowed:
            raise func(
                "Vous avez entré un nombre total de bateaux trop élevé par rapport à la taille du plateau. \n{} bateaux sont autorisés au maximum.".format(self.nb_ships_allowed))

        # Vérification qu'il n'y a pas nb_ships_taille_sup > nb_ships_taille_inf.
        for x, y in zip(boat_list, boat_list[1:]):
            if x < y:
                raise func(
                    "Vous avez plus de bateaux de taille {} que de bateaux de taille {}.\n> ".format(y, x))    
        return boat_list
        
    def verif_config_input(self, func, num_conf, config_list):
        """Vérification que les inputs des bateaux sont corrects.
        
        Args:
            func (function): Fonction qui gère les erreurs.
            num_conf (int): Ligne choisie.
            config_list (list): Liste des configurations.
            
        Returns:
            self.config (dict): Fichier de configuration.
            
        Raises:
            func: Erreurs des inputs sur le cmd (parser.error) ou de l'utilisateur (ValueError).
            
        .. seealso:: ships_number_rule().
        """

        # Liste de tuples contenant la configuration choisie
        config_sorted = config_list[num_conf - 1]

        # Tests pour vérifier que la configuration est valide
        if config_sorted[0][1] > 26 or config_sorted[0][1] < 10:
            raise func(
                "Configuration choisie invalide. \nLe nombre de colonnes doit être un entier compris entre 10 et 26. \nModifier le fichier de configuration correspondant.\n")
        else:
            self.config["columns"] = config_sorted[0][1]
        if config_sorted[1][1] > 26 or config_sorted[1][1] < 10:
            raise func(
                "Configuration choisie invalide. \nLe nombre de lignes doit être un entier compris entre 10 et 26. \nModifier le fichier de configuration correspondant.\n")
        else:
            self.config["lines"] = config_sorted[1][1]
            
        # Nombre de bateaux autorisés
        self.ships_number_rule()
        # Test d'un nombre de bateaux valide
        self.nb_tot_ships = sum([i for i in config_sorted[2][1].values()])

        if self.nb_tot_ships > self.nb_ships_allowed:
            raise func(
                "Configuration choisie invalide. \nVous avez un nombre total de bateaux trop élevé par rapport à la taille du plateau. \n{} bateaux sont autorisés au maximum. \nModifier le fichier de configuration correspondant.\n".format(self.nb_ships_allowed))

        # Vérification qu'il n'y a pas nb_ships_taille_sup > nb_ships_taille_inf.
        for i in range(3):
            if config_sorted[2][1][i + 2] < config_sorted[2][1][i + 3]:
                raise func(
                    "Configuration choisie invalide. \nVous avez plus de bateaux de taille {} que de bateaux de taille {}. \nModifier le fichier de configuration correspondant.\n".format(i + 3, i + 2))
                break
        self.config["ships"] = config_sorted[2][1]
    
    def verif_parser(self, args, parser):
        """Vérification des entrées en ligne de commande.
        
        Args:
            args (class instance): Argument entrés en ligne de commande.
            parser (class instance): Parser de la ligne de commande.
            
        Returns:
            self.config (dict): Fichier de configuration.
            
        Raises:
            parser.error: Erreurs des inputs sur le cmd.
            
        .. seealso:: ships_number_rule(), verif_boat_input(), verif_config_input().
        """

        # Deux attributs exclusifs
        if hasattr(args, 'columns'):
            self.config["columns"] = args.columns
            self.config["lines"] = args.lines
            # Nombre de bateaux autorisés
            self.ships_number_rule()
            # Liste des bateaux
            args.boat = list(map(int, args.boat.split(',')))
            # Vérification que les inputs des bateaux sont corrects
            args.boat = self.verif_boat_input(parser.error, args.boat)
            self.config["ships"] = {2: args.boat[0], 3: args.boat[1], 4: args.boat[2], 5: args.boat[3]}
        elif args.exist_config is not None:
            # Lecture du fichier de configuration
            config_list = self.read_config()
            if not args.exist_config in range(1, len(config_list) + 1):
                raise parser.error("Entrer un nombre compris entre 1 et {}.".format(len(config_list)))
            # Vérification que les inputs des bateaux sont corrects
            self.verif_config_input(parser.error, args.exist_config, config_list)
            
    def new_configuration(self):
        """Cré une configuration contenant la taille du plateau, le nombre de bateaux et
        leur taille.

         - Test des différentes entrées 'columns' et 'lines' comprises entre 10 et 26.
         - Test d'entrée du nombre de bateaux et de leur taille en respectant 'ships_number_rule(config)'.
         - Tri de 'config' et écriture dans 'file_name' s'il n'y est pas déjà.

        Returns:
            self.nb_tot_ships (int): Nombre total de bateaux.
            self.config (dict): Fichier de configuration.

        Raises:
            ValueError: Erreurs des inputs.

        .. seealso:: columns_input(), lines_input(), ships_input(), add_config().
        """

        # Tests des inputs du nb_lines,nb_columns, nb_bateaux
        self.config["columns"] = Configuration.columns_input()
        self.config["lines"] = Configuration.lines_input()
        ships_values = self.ships_input()
        self.config["ships"] = {2: ships_values[0], 3: ships_values[1], 4: ships_values[2], 5: ships_values[3]}
        # Ajout de la configuration crée au fichier
        self.add_config()
    
    @classmethod
    @while_true
    def columns_input(cls):
        """Input du nombre de colonnes.
        
        Returns:
            columns (int): Le nombre de colonnes.
        """
        
        columns = int(input('\nEntrer le nombre de colones (10-26): \n> '))
        if not(10 <= columns <= 26):
            raise ValueError("Le nombre de colonnes doit être un entier compris entre 10 et 26.\n")
        return columns
    
    @classmethod
    @while_true
    def lines_input(cls):
        """Input du nombre de lignes.
        
        Returns:
            lines (int): Le nombre de lignes.
        """
        
        lines = int(input('\nEntrer le nombre de lignes (10-26): \n> '))
        if not(10 <= lines <= 26):
            raise ValueError("Le nombre de lignes doit être un entier compris entre 10 et 26.\n")
        return lines
    
    @while_true
    def ships_input(self):
        """Input du nombre de bateaux.
        
        Returns:
            ships_values (list): Le nombre de bateaux de différentes tailles.
            self.nb_tot_ships (int): Nombre total de bateaux.
            
        .. seealso:: ships_number_rule().
        """
        
        self.ships_number_rule() # Nombre de bateaux autorisés
        ships_values = list(map(int, input(
            "\nEntrer à la suite les nombres de bateaux de tailles 2,3,4 et 5 séparés par une virgule. \n{} bateaux sont autorisés au maximum.\n> ".format(self.nb_ships_allowed)).split(',')))
        ships_values = self.verif_boat_input(ValueError, ships_values, verif=True)   
        
        return ships_values

    def add_config(self):
        """Ajoute la configuration créée au fichier.
        
        Args:
            self.config (dict): Fichier de configuration.
        
        .. seealso:: read_config().
        """

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

    def choose_config(self):
        """Configuration d'une partie par l'utilisateur ou utilisation d'une configuration existante.

        .. seealso:: conf_choose_input(), conf_input().
        """

        conf = Configuration.conf_choose_input()

        if conf == 1:
            print("\nVeuillez remplir les paramètres de la configuration de la partie à laquelle vous allez jouer.")
            # Fichier de configuration commun aux deux joueurs
            self.new_configuration()
        elif conf == 2:
            self.conf_input()
            print("\nContenu du fichier de configuration choisi : \n",self.config, "\n")
    
    @classmethod
    @while_true
    def conf_choose_input(cls):
        """Input du choix de la configuration.
        
        Returns:
            conf (int): Choix.
        """
        
        print("\nChoix de la configuration :")
        conf = int(
            input("1. Créer une nouvelle configuration,\n2. Utiliser une configuration existante,\n> "))
        if not conf in [1, 2]:
            raise ValueError("Entrer 1 ou 2.\n> \n> ")
        return conf
        
    @staticmethod
    @while_true
    def conf_line_input(config_list):
        """Input de la ligne contenant la configuration.
        
        Args:
            config_list (list): Liste des configurations.
            
        Returns:
            num_conf (int): Ligne.
        """
        
        num_conf = int(input(
            "\nEntrer le nombre correspondant à la ligne de la configuration que vous voulez entrer :\n> "))
        if not num_conf in range(1, len(config_list) + 1):
            raise ValueError(
                "Entrer un nombre compris entre 1 et {}.\n> ".format(len(config_list)))
        return num_conf
    
    @while_true
    def conf_input(self):
        """Choix de l'action à effecter concernant la configuration.
        
        .. seealso:: read_config(), conf_line_input(), verif_config_input(), new_configuration().
        """
        
        config_list = self.read_config()
        if config_list: # S'il y a des configurations
            num_conf = Configuration.conf_line_input(config_list)
            self.verif_config_input(ValueError, num_conf, config_list)
        else:
            print("Le fichier ne contient aucune configuration.")
            self.new_configuration()
    
    @while_true
    def choose_gamemode(self):
        """Choix du mode de jeu PVP ou PVE.

        Returns:
            self.mode: Mode de jeu.
        """

        # Mode de jeu 2 joueurs ou contre l'IA
        print("\nChoix du mode jeux (PVP, PVE):")
        self.mode = int(
            input("1. Joueur contre joueur,\n2. Joueur contre IA,\n> "))
        if not self.mode in [1, 2, 3]:
            raise ValueError("Entrer 1 ou 2.\n> ")
        
    @while_true
    def choose_file(self):
        """Choix d'un fichier contenant déjà des configurations.

        Returns:
            self.file_name (str): Nom du fichier.

        .. seealso:: isalnum(), confirm_input().
        """

        self.file_name = input("\nEntrer le nom du fichier de configuration(lettres/chiffres), en cas de mauvaise entrée le fichier 'configs' est défini par défaut.\nVous pouvez entrer ce fichier si vous ne comprenez pas cet input.\n> ")
        if not self.file_name.isalnum():
            self.file_name = 'configs'
        if not self.confirm_input():
            return 'verif'

    def read_config(self):
        """Lit le fichier de configuration config.txt situé dans le même dossier ou le cré.

        Extrait la liste des configurations.
        Affiche les configurations que l'utilisateur peut choisir.

        Returns:
            config_list_sorted (list): Configurations du fichier triées.
            self.file_name (str): Nom du fichier contenant la configuration avec extension '.txt'.

        .. seealso:: os.path.exists(), ast.literal_eval(), splitlines().
        """

        config_list_sorted = []

        if os.path.exists(self.file_name):
            with open(self.file_name, 'r') as f:
                print("\nFichier contenant la configuration :", f.name)
                data = f.read()

            config_list = [ast.literal_eval(line) for line in data.splitlines()] # Liste des configurations
            config_list_sorted = [sorted(config_list[i]) for i, j in enumerate(config_list)] # Tri de la configuration
            # Affichage des configurations
            print("Configurations présentes dans le fichier.")
            for i in config_list_sorted:
                print(i)
        else:
            print('Le fichier n\'existe pas. Création d\'un fichier de configuration.\n')
            f = open(self.file_name, "w")
            f.close()

        return config_list_sorted

    def ships_number_rule(self):
        """ Vérifie que le nombre total de bateaux n'est pas trop élevé.
        
        Args:
            self.config (dict): Fichier de configuration.
            
        Returns:
            self.nb_ships_allowed (int): Nombre de bateaux autorisés.

        .. seealso:: math.sqrt().
        """

        # Tableau des nb de colones/lignes possibles
        liste_coord = [i for i in range(10, 27)]
        # Multiplication croisée, remove duplicates, tri par ordre croissant.
        prod_liste_coord = sorted(list({i * j for i in liste_coord for j in liste_coord}))
        # Affichage 0 si c'est une puissance entière
        sqrt_prod_liste_coord = [(math.sqrt(i) % 2) for i in prod_liste_coord]
        # Trouve l'emplacement des 0
        indices = [i for i, x in enumerate(sqrt_prod_liste_coord) if x == 0]

        nb_tot_cases = self.config["lines"] * self.config["columns"]  # Nombre de cases total

        self.nb_ships_allowed = 5  # Nombre de bateaux minimum (10*10)
        for i in indices:
            if prod_liste_coord.index(nb_tot_cases) >= i:
                self.nb_ships_allowed += 1
        self.nb_ships_allowed -= 1
    
    @staticmethod
    def confirm_input():
        """Demande de confirmer l'entrée.
        
        Returns:
            boolean value: Si on confirme ou non.
        """

        verif = input("Valider la sélection (O/N): ")
        if not verif in ["O", "N"]:
            raise ValueError("Entrer O ou N.")
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
        """Affichage de la classe. """
        return self.__str__()


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
        # Lettres minuscules
        alph = list(string.ascii_lowercase)

        for k in range(nb_tot_ships):
            letter = alph[k] # Lettre correspondant au bateau
            restart = True
            while restart:  # Boucle infini pour répéter lorsqu'il y a une mauvaise entrée ou un bateau déjà présent
                restart = False
                placed = False  # Variable True si un bateau complet à été placé
                if joueur.aleatoire == True:
                    taille, place, direction, taille_list = self.alea_input_rules(configships, table, taille_list)
                else:
                    taille, place, direction = self.user_input_rules(configships, table)
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
                        restart, placed = self.placement_boat_sub(joueur, config, taille, deplacement, i, restart, placed, letter)
                        if placed:
                            # On décrémente de 1 le nb de bateaux de cette taille
                            configships[taille] -= 1
                            restant -= 1
                            if not joueur.aleatoire:
                                print("Votre bateau est bien placé.")
                                print("Il vous reste {} bateaux de taille {}.".format(
                                    configships[taille], taille))
                                print(
                                    "Il vous reste {} bateaux à placer.".format(restant))

    def placement_boat_sub(self, joueur, config, taille,
                             deplacement, i, restart, placed, letter):
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
            letter (str): Lettre de l'alphabet.

        Returns:
            restart (boolean): Si l'on recommence la boucle en cas de mauvais placement.
            placed (boolean): Si le bateau complet est posé.
            self.list_cases (class): Objet représentant une case.
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
            self.list_cases[i + deplacement[0] * j].our_ship = str(taille) + letter
            placed = True

        return restart, placed

    def test_directions(self, config, taille, direction, i):
        """Test de si le bateau se trouve hors plateau.

        Args:
            self.list_cases (class): Objet représentant une case.
            config (dict): Fichier de configuration.
            taille (int): Taille du bateau.
            direction (str): Direction du bateau.
            i (int): Emplacement initial du bateau.

        Returns:
            deplacement (list): Déplacement d'une unité réalisé en fonction de la direction choisie et valeur booléenne décrivant si l'on sort ou non du plateau.
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
        """Retourne s'il y a des bateaux sur les cases adjacentes d'un bateau.

        Args:
            config (dict): Fichier de configuration.
            taille (int): Taille du bateau.
            deplacement (tuple): Déplacement d'une unité réalisé en fonction de la direction choisie et valeur booléenne décrivant si l'on sort ou non du plateau.
            i (int): Emplacement initial du bateau.

        Returns:
            test_cases_autour_boat (boolean): S'il n'y a pas de bateaux autour de la case.

        .. seealso:: near_cases().
        """

        cases_autour_boat = []

        for j in range(taille + 2):
            cases_autour_boat.extend(self.near_cases(config, i + deplacement[0] * j))

        test_cases_autour_boat = len(cases_autour_boat) != cases_autour_boat.count(0) + cases_autour_boat.count(taille) or cases_autour_boat.count(taille) > taille

        return test_cases_autour_boat

    def near_cases(self, config, place, tir=None):
        """ Regarde s'il y a des bateaux sur les cases adjacentes d'une case

        Args:
            config (dict): Fichier de configuration.
            place (int): Emplacement de la case bateau.
            tir (str): Pour retourner si l'on a tiré autour de la case

        Returns:
            cases_autour (list): Liste des cases autour d'une case bateau.

        Raises:
            IndexError: Emplacement qui n'est pas présent dans le tableau.
        """

        cases_autour = []

        for i in [- config["columns"], config["columns"], 1, - 1]:
            try:
                if tir == 'our':
                    cases_autour.append(self.list_cases[place + i].our_tir)
                else:
                    cases_autour.append(self.list_cases[place + i].our_ship)
            except IndexError:
                cases_autour.append(0)

        return cases_autour

    def affichage_our_ships(self, config):
        """Affichage des bateaux du joueur et des attaques de l'adversaire.

        Args:
            config (dict): Fichier de configuration.
            
        .. seealso:: sub_affichage().
        """

        print("Bateaux du joueur :")
        j_ships = [self.list_cases[i].our_ship for i in range(0, config["lines"] * config["columns"])]
        # Affichage d'une croix sur la case touchée
        for i, j in enumerate(j_ships):
            if j != 0 and int(self.list_cases[i].adv_tir) == 1:
                j_ships[i] = 'x'

        self.sub_affichage(config, j_ships)
        print("Tirs de l'adversaire :")
        adv_tir = [int(self.list_cases[i].adv_tir) for i in range(0, config["lines"] * config["columns"])]
        self.sub_affichage(config, adv_tir)

    def affichage_our_tir(self, config):
        """ Affichage de là ou a tiré le joueur.

        Args:
            config (dict): Fichier de configuration.
        """

        print("Tirs du joueur :")
        j_fire = [int(self.list_cases[i].our_tir) for i in range(0, config["lines"] * config["columns"])]
        self.sub_affichage(config, j_fire)

    def sub_affichage(self, config, attr):
        """ Affichage formaté avec pandas.

        Args:
            config (dict): Fichier de configuration.
            attr (list): Liste d'attributs à afficher.
        
        .. seealso:: apndas.DataFrame().
        """

        # Création d'un array pour l'affichage
        tab = np.array([attr[i:i + config["columns"]] for i in range(0, config["lines"] * config["columns"], config["columns"])])
        # Affichage avec le module pandas
        pandas.set_option('expand_frame_repr', False)
        pandas.set_option('max_colwidth', 5)
        pandas.set_option('display.max_columns', 26)
        print(pandas.DataFrame(tab, self.abscisses, self.ordonnes))

    def gen_coordonnees(self, config):
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
        self.ordonnes = list(string.ascii_uppercase[:config["columns"]])
        # En abscisse les chiffres correspondant
        self.abscisses = [str(i) for i in range(config["lines"])]
        # On transforme les couples lettre/chiffre en string
        table = ["".join(value) for value in list(itertools.product(self.ordonnes, self.abscisses))]

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

        Raises:
            ValueError: Erreurs des inputs.
            
        .. seealso:: taille_input(), place_input(), direction_input().
        """

        taille = Plateau.taille_input(configships)
        place = Plateau.place_input()
        direction = Plateau.direction_input()

        return taille, place, direction
    
    @staticmethod
    @while_true
    def taille_input(configships):
        """Input de la taille du bateau.
        
        Returns:
            taille (int): Taille du bateau.
        """
        
        taille = int(input(
            "Entrer la taille de votre bateau (1-{}): ".format(len(configships.keys()) + 1)))
        if not taille in sorted([i for i in configships.keys()]):
            raise ValueError("Entrer un entier compris entre 1 et {}.".format(
                len(configships.keys()) + 1))
        elif configships[taille] == 0:
            raise ValueError(
                "Vous n'avez plus de bateau de taille {}.".format(taille))
        return taille
    
    @classmethod
    @while_true
    def place_input(cls):
        """Input de la première case du bateau.
        
        Returns:
            place (str): Emplacement d'une de ses extrémités.
        """
        
        place = input("Entrer la première case de votre bateau : ")
        if not place in table:
            raise ValueError(
                "Entrer une case qui est présente sur le plateau.")
        return place
    
    @classmethod
    @while_true
    def direction_input(self):  
        """Input de la direction vers laquelle se dirige le bateau.
        
        Returns:
            direction (str): Direction du bateau.
        """
        
        direction = input(
            "Entrer la direction vers laquelle se dirige votre navire (N/S/E/O) : ")
        if not direction in ['N', 'S', 'E', 'O']:
            raise ValueError("Entrer une direction valide.")
        return direction
        
    def alea_input_rules(self, configships, table, taille_list):
        """Choix aléatoire.

        Args:
            configships (dict): Copie des bateaux du fichier de configuration. Décrémentée du bateau placé.
            table (list): Coordonnées de toutes les cases du plateau.
            taille_list (list): Listes des tailles possibles.

        Returns:
            taille (int): Taille du bateau.
            place (str): Emplacement d'une de ses extrémités.
            direction (str): Direction du bateau.
            taille_list (list): Liste des tailles disonibles.
            
        .. seealso:: taille_alea_input().
        """

        taille, taille_list = Plateau.taille_alea_input(taille_list, configships)        
        place = secrets.choice(table)
        direction = secrets.choice(['N', 'S', 'E', 'O'])

        return taille, place, direction, taille_list
    
    @staticmethod
    @while_true
    def taille_alea_input(taille_list, configships):
        """Choix aléatoire de la taille du bateau.
        
        Returns:
            taille (int): Taille du bateau.
            taille_list (list): Liste des tailles disonibles.
        """
        
        taille = secrets.choice(taille_list)
        if configships[taille] == 0:
            taille_list.remove(taille)
            raise ValueError
        return taille, taille_list

    def __str__(self):
        """Affichage de tous les attributs de la classe.

        Returns:
            list_cases (list): Liste des objets Case().
        """

        return "Liste des objets Case(): {}\n".format(self.list_cases)


class Player(object):
    """Classe représentant un joueur.

    Attributes:
        name (str): Nom du joueur.
        plateau (list): Cases du plateau du joueur.
        start (boolean): A commencé où non la partie.
        tir (int): Nombre de tirs effectués.
        ships_left (int): Nombre de bateaux restant.
        ships_lose (int): Nombre de bateaux perdus.
        ships_hit (int): Nombre de cases bateaux touchées.
        aleatoire (boolean): Variable utile au placement.
        IA (class instance): IA derrière le joueur.
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
        self.IA = None # IA du joueur s'il n'est pas humain    
    
    @while_true
    def joueur_name_input(self, j_type):
        """Choix aléatoire de la taille du bateau.
        
        Args:
            j_type (str): Message correspondant au joueur.
            
        Returns:
            self.name name (str): Nom du joueur.
        """
        
        self.name = input(
            "Enter le nom {joueur} (20 caractères maximum):\n> ".format(joueur=j_type))
        if len(self.name) > 20:
            raise ValueError("Entrer un nom plus court.")
        elif not self.name.strip():
            raise ValueError("Entrer un nom valide.")
        
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

        return "Nom : {},\nA commencé la partie : {},\nNombre de tirs effectués : {},\nNombre de bateaux restant : {},\nNombre de bateaux coulés : {},\nNombre de cases bateau touchées : {},\nValeur du placement aléatoire : {}\n".format(
            self.name, self.start, self.tir, self.ships_left, self.ships_lose, self.ships_hit, self.aleatoire)


class PlayerHuman(Player):
    """Classe représentant un joueur humain.

    Attributes:
        (Hérite des attributs de la classe Player().)
    """

    def __init__(self, conf, plateau_joueur):
        """Constructeur de la classe.
        On reprend le constructeur de Player().
        
        .. seealso:: gen_human(), StrategieIA().
        """

        super().__init__(conf, plateau_joueur)
        self.aleatoire = False
        self.gen_human(conf.config, conf.nb_tot_ships, Plateau.table, plateau_joueur)
        self.IA = StrategieIA(conf, human=True) # IA latente qui ne fait qu'un record des possibilités
        # Utilité pour un passage joueur - IA en cours de partie ?

    def gen_human(self, config, nb_tot_ships, table, plateau_joueur):
        """Génère le plateau et les attributs d'un joueur.

        Args:
            config (dict): Fichier de configuration.
            nb_tot_ships (int): Nombre total de bateaux.
            table (list): Coordonnées de toutes les cases du plateau.
            plateau_joueur (list): Plateau du joueur.

        Returns:
            self.plateau: Plateau avec bateaux.

        .. seealso:: joueur_name_input(), generation_input(), placement_boat(), near_input(), affichage_our_ships().
        """
        
        self.joueur_name_input('du joueur')
        self.ships_left = nb_tot_ships

        print("\nChoix du mode de génération de l'emplacement des bateaux pour {joueur1}:".format(
            joueur1=self.name))
        gen_j1 = PlayerHuman.generation_input()

        if gen_j1 == 1:
            # Génération du plateau du joueur 1 par le joueur 1
            plateau_joueur.placement_boat(self, nb_tot_ships, config, table)
        elif gen_j1 == 2:
            # On mets temporairement self.aleatoire à True
            self.aleatoire = True
            # Génération du plateau du joueur 1 aléatoirement
            cote = PlayerHuman.near_input()
            if cote == 1:
                plateau_joueur.placement_boat(self, nb_tot_ships, config, table)
            elif cote == 2:
                plateau_joueur.placement_boat(self, nb_tot_ships, config, table, near=False)
            self.aleatoire = False
        plateau_joueur.affichage_our_ships(config)
    
    @classmethod
    @while_true
    def generation_input(cls):
        """Input du choix de la génération du plateau.
        
        Returns:
            gen_j1 (int): Par le joueur ou aléatoire.
        """
        
        gen_j1 = int(
            input("1. Génération par le joueur,\n2. Génération aléatoire,\n> "))
        if not gen_j1 in [1, 2]:
            raise ValueError("Entrer 1 ou 2.")
        return gen_j1
    
    @classmethod
    @while_true
    def near_input(cls):
        """Input du choix du placement proche des bateaux.
        
        Returns:
            cote (int): Autoriser côte à côte ou non.
        """
        
        cote = int(
            input("1. Autoriser les bateaux côtes à côtes,\n2. Ne pas autoriser les bateaux côtes à côtes,\n> "))
        if not cote in [1, 2]:
            raise ValueError("Entrer 1 ou 2.")
        return cote


class PlayerIA(Player):
    """Classe représentant un joueur IA.

    Attributes:
        (Hérite des attributs de la classe Player().)
    """

    def __init__(self, conf, plateau_joueur, init=None):
        """Constructeur de la classe.
        On reprend le constructeur de Player().
        
        .. seealso:: joueur_name_input(), StrategieIA(), quadrillage_list(), placement_boat(), affichage_our_ships().
        """

        super().__init__(conf, plateau_joueur)
        self.ships_left = conf.nb_tot_ships
        self.aleatoire = True
        if init is None:
            self.joueur_name_input('de l\'IA')
            self.IA = StrategieIA(conf)
        elif init:
            self.name = init[0]
            self.IA = StrategieIA(conf, human=True)
            self.IA.difficulte = init[1] # Attribution de la difficulté
            # duplicates
            if self.IA.difficulte == 2:
                self.IA.quadrillage_list(conf.config) # Une case sur deux
        plateau_joueur.placement_boat(self, conf.nb_tot_ships, conf.config, Plateau.table)
        plateau_joueur.affichage_our_ships(conf.config)


class StrategieIA(object):
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

    def __init__(self, conf, human=False):
        """Constructeur de la classe.

        Initialisation des différents paramètres se retrouvant tour après tour.
        
        .. seealso:: choose_difficulte(), quadrillage_list().
        """

        if not human: # Si ce n'est pas un joueur, on attribut une difficulté
            self.choose_difficulte()
        else:
            self.difficulte = None

        conf.difficulte_IA = self.difficulte

        self.table_allowed = np.array(Plateau.table.copy()) # Array numpy pour qu'une modification sur table_allowed modifie aussi table_allowed_cut
        self.table_allowed_cut = np.array([])

        self.possibilites = []
        self.horizontal = False
        self.vertical = False
        self.direct = ['N', 'S', 'E', 'O']
        self.directions = self.direct.copy()
        
        # duplicates
        if self.difficulte == 2:
            self.quadrillage_list(conf.config) # Une case sur deux
    
    @while_true
    def choose_difficulte(self):
        """Choix par l'utilisateur de la difficulté de l'IA.
        
        Returns:
            self.difficulte (int): Difficulté de l'IA.
        """
        
        self.difficulte = int(
            input("Choisissez la difficulté de l'IA :\n 0. Très facile\n 1. Facile\n 2. Moyenne\n 3. Difficile\n> "))
        if not self.difficulte in range(4):
            raise ValueError("Entrer une valeur comprise entre 0 et 3.")

    def quadrillage_list(self, config):
        """Découpage de la liste des cases pour correspondre à un quadrillage du plateau.

        Args:
            config (dict): Fichier de configuration.
        Returns:
            self.table_allowed_cut (array): Liste des cases quadrillée.
        """

        table_cut = Plateau.table.copy()
        # Sépare de 10 en 10
        table_cut = [table_cut[i:i + config["columns"]] for i in range(0, len(table_cut), config["columns"])]
        # Alterne pair/impair
        table_cut = [item[::2] if index % 2 == 0 else item[1::2] for index, item in enumerate(table_cut)]
        # On rattache les sous-listes
        self.table_allowed_cut = np.array([x for y in table_cut for x in y])

    def exec_strategie(self, joueur1, joueur2, config):
        """Exécute la stratégie correspondant à la difficulté donnée à l'IA.

        Args:
            Attributs de la classe correspondant à la fonction appelée.
            
        .. seealso:: strategie_alea(), strategie_naive().
        """

        if self.difficulte == 0:
            position = self.strategie_alea()
        elif self.difficulte in [1,2]:
            position = self.strategie_naive(joueur1, joueur2, config)

        return position

    def strategie_alea(self):
        """Stratégie complètement aléatoire.

        Args:
            self.table_allowed (array): Coordonnées des cases qui ne sont pas encore jouées.

        Returns:
            self.table_allowed (array): Coordonnées des cases qui ne sont pas encore jouées.
            self.position (str): Coordonnée de la case visée.
        """

        position = np.random.choice(self.table_allowed)
        index = np.argwhere(self.table_allowed == position)
        self.table_allowed = np.delete(self.table_allowed, index)

        return position

    def strategie_naive(self, joueur1, joueur2, config):
        """Stratégie de jeu de l'IA: un bateau à la fois.

        Recherche de bateaux sur les cases adjacentes si case bateau touchée.
        Quand trouvé, continuer sur la même ligne.
        Quand il n'y en a plus, s'arrêter : passer de l'autre côté ou retourner aléatoire si bateau coulé.

        Args:
            joueur1 (class instance): Instance de la classe Player() du joueur 1.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.
            config (dict): Fichier de configuration.
            self.table_allowed_cut (array): Coordonnées des cases qui ne sont pas encore jouées coupées en fonction de la difficulté.
            self.table_allowed (array): Coordonnées des cases qui ne sont pas encore jouées.
            self.horizontal (boolean): Si le bateau est orienté Est/Ouest.
            self.vertical (boolean): Si le bateau est orienté Nord/Sud.
            self.directions (list): Directions restreintes possibles.
            self.direct (list): Toutes directions possibles.

        Returns:
            joueur1 (class instance): Instance de la classe Player() du joueur 1.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.
            self.table_allowed_cut (array): Coordonnées des cases qui ne sont pas encore jouées coupées en fonction de la difficulté.
            self.table_allowed (array): Coordonnées des cases qui ne sont pas encore jouées.
            position (str): Coordonnée de la case visée.
            self.horizontal (boolean): Si le bateau est orienté Est/Ouest.
            self.vertical (boolean): Si le bateau est orienté Nord/Sud.
            self.directions (list): Directions restreintes possibles.

        .. seealso:: operator.itemgetter(), choose_direction(), give_direction(), test_directions().
        """
        
        if not self.possibilites:  # Test liste vide
            # Choix aléatoire dans les cases possibles.
            if self.table_allowed_cut.size == 0: # Pas de liste prédéfinie
                position = np.random.choice(self.table_allowed)
            else:
                position = np.random.choice(self.table_allowed_cut)
        else:
            # Index et longueur de la sous-liste la plus grande dans self.possibilites
            self.index = max(enumerate([len(sublist) for sublist in self.possibilites]), key=operator.itemgetter(1))[0]
            # Liste des coordonnées de la sous-liste
            subposs = [x[0] for x in self.possibilites[self.index]]
            
            if len(self.possibilites[self.index]) == 1:
                case_bateau = subposs[0]
                self.choose_direction(config, case_bateau, joueur2)
                direction = secrets.choice(self.directions)
            else:
                # Test deux cases bateau adjacentes
                if len(self.possibilites[self.index]) == 2:
                    # Vérifier les 2 premiers éléments de la sous-liste
                    if subposs[0] + 1 == subposs[1]:
                        self.horizontal = True
                    elif subposs[0] + config["columns"] == subposs[1]:
                        self.vertical = True

                # Liste des positions extrêmes de la liste
                extrem = [subposs[0], subposs[-1]]
                # Choix aléatoire d'une position
                indice = secrets.choice([0,1])
                # Cased bateau choisie
                case_bateau = extrem[indice]
                
                # On essaye avec l'autre case si la liste des directions est vide
                while True:
                    try:
                        print(case_bateau)
                        direction = self.give_direction(config, joueur2, case_bateau)
                        break
                    except IndexError:
                        case_bateau = extrem[(indice + 1)% 2]
                        print(case_bateau)
                        direction = self.give_direction(config, joueur2, case_bateau)

            # On attribut la position de tir
            position = joueur2.plateau.list_cases[case_bateau + joueur2.plateau.test_directions(config, 2, direction, case_bateau)[0]].coordonnees

        # On enlève la position des listes de coordonnées
        ind = np.argwhere(self.table_allowed == position)
        self.table_allowed = np.delete(self.table_allowed, ind)
        ind = np.argwhere(self.table_allowed_cut == position)
        self.table_allowed_cut = np.delete(self.table_allowed_cut, ind)

        return position

    def give_direction(self, config, joueur2, case_bateau):
        """Donne la direction du tir.

        Args:
            self.horizontal (boolean): Si le bateau est orienté Est/Ouest.
            self.vertical (boolean): Si le bateau est orienté Nord/Sud.
            self.directions (list): Directions restreintes possibles.
            config (dict): Fichier de configuration.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.
            case_bateau (int): Index de la case adjacente de celle sur laquelle on veut tirer.

        Returns:
            direction (str): Direction du tir.

        .. seealso:: choose_direction().
        """

        self.choose_direction(config, case_bateau, joueur2)

        if self.horizontal:  # Test 2 éléments côtes à côtes
            # Intersection des deux sets
            direction = secrets.choice(list(set(self.direct[2:]).intersection(set(self.directions))))
        elif self.vertical:  # Test 2 éléments l'un en dessous de l'autre
            # Intersection des deux sets
            direction = secrets.choice(list(set(self.direct[:2]).intersection(set(self.directions))))

        return direction

    def choose_direction(self, config, case_bateau, joueur2):
        """Trouve les directions valides pour le tir suivant.

        Args:
            config (dict): Fichier de configuration.
            case_bateau (int): Index de la case adjacente de celle sur laquelle on veut tirer.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.

        Returns:
            self.directions (list): Directions utilisables.

        .. seealso:: test_directions(), near_cases().
        """
        
        # Set des directions pour lesquelles on ne sort pas du plateau autour de la case poss.
        out_directions = set({direction : joueur2.plateau.test_directions(
                            config, 2, direction, case_bateau)[1] for direction in self.direct if joueur2.plateau.test_directions(
                            config, 2, direction, case_bateau)[1] == False}.keys())
        # Set des cases autour de la position contenant un tir ([N,S,E,O]), O sans tir ou en dehors du plateau.
        cases_autour = joueur2.plateau.near_cases(config, case_bateau, tir = 'our')
        near_ship = set({direction : cases_autour[i] for i, direction in enumerate(self.direct) if cases_autour[i] != 0}.keys())
        # On enlève la direction s'il y a un tir
        self.directions = list(out_directions - near_ship)

    def cases_possibles(self, joueur1, joueur2):
        """Retourne les cases autour desquelles on a une chance de toucher un bateau.

        Args:
            joueur1 (class instance): Instance de la classe Player() du joueur 1.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.

        Returns:
            self.possibilites (list): Liste de tuples contenant les coordonnées des bateaux ennemis touchés et leur taille.

        .. seealso:: zip(), itertools.groupby(), operator.itemgetter().
        """

        # Index des bateaux adverses
        poss = sorted(list({i for i in range(len(joueur2.plateau.list_cases)) if joueur2.plateau.list_cases[i].adv_ship == True}))
        # Taille du bateau correspondant à l'index
        boat = [joueur1.plateau.list_cases[i].our_ship for i in range(len(joueur1.plateau.list_cases)) if i in poss]

        # Cré une liste de tuples
        self.possibilites = list(zip(poss, boat))
        # Trie les tuples en fonction de la taille du bateau
        self.possibilites.sort(key=lambda tup: tup[1])
        # Groupe les bateaux de même taille dans une sous-liste
        self.possibilites = [list(group) for key, group in itertools.groupby(self.possibilites,operator.itemgetter(1))]
        # Trie les tuples dans les sous-listes en fonction de la position
        [sublist.sort(key=lambda tup: tup[0]) for sublist in self.possibilites]
        # Trie les sous-listes en fonction de leur taille
        self.possibilites.sort(key=len)
        # Exemple de retour: [[(65, 2)], [(13, 3)], [(11, 4), (12, 4)]]

    def boat_sink(self, joueur1, joueur2):
        """Regarde si un bateau est coulé.

        Args:
            self.possibilites (list): Liste de tuples contenant les coordonnées des bateaux ennemis touchés et leur taille.
            joueur1 (class instance): Instance de la classe Player() du joueur 1.
            joueur2 (class instance): Instance de la classe Player() du joueur 2.

        Returns:
            self.possibilites (list): On enlève les bateaux coulés.
            self.directions, self.horizontal, self.vertical : On réinitialise les variables.
            joueur1 (class instance): On comptabile les bateaux restants et perdus.
        """
        
        # Test bateau coulé
        if self.possibilites and int(self.possibilites[-1][0][1][0]) == len(self.possibilites[-1]):
            joueur1.ships_left -= 1
            joueur1.ships_lose += 1
            self.directions = self.direct.copy()
            self.horizontal, self.vertical = False, False
            for sublist in self.possibilites[-1]:
                # Emplacement dans possibilites des valeurs puis remplacement valeurs dans joueur2.plateau
                joueur2.plateau.list_cases[sublist[0]].adv_ship = int(sublist[1][0])
            self.possibilites.remove(self.possibilites[-1])

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

        return "Difficulté : {},\nCoordonnées libres : {},\nCase contenant un bateau : {},\nOrientation horizontale : {},\nOrientation verticale : {},\nToutes les directions : {},\nDirections possibles : {},\n".format(
                self.difficulte, self.table_allowed, self.possibilites, self.horizontal, self.vertical, self.direct, self.directions)


class Battleship(object):
    """Classe définissant le jeu en lui même.

    Attributes:
        joueur1 (class instance): Instance de la classe Player() du joueur 1.
        joueur2 (class instance): Instance de la classe Player() du joueur 2.
        conf (class instance): Instance de la classe Configuration().
    """

    def __init__(self, args, parser):
        """Constructeur de la classe.
        
        Args:
            args (class instance): Argument entrés en ligne de commande.
            parser (class instance): Parser de la ligne de commande.
        
        .. seealso:: Configuration(), Plateau(), PlayerHuman(), PlayerIA(), choose_starter(), play(), choose_number_plays().
        """

        self.conf = Configuration(args, parser)

        plateau_joueur1 = Plateau(self.conf.config)
        plateau_joueur2 = Plateau(self.conf.config)

        if self.conf.mode != 3:
            if self.conf.mode == 1:
                self.joueur1 = PlayerHuman(self.conf, plateau_joueur1)
                self.joueur2 = PlayerHuman(self.conf, plateau_joueur2)
            elif self.conf.mode == 2:
                self.joueur1 = PlayerHuman(self.conf, plateau_joueur1)
                self.joueur2 = PlayerIA(self.conf, plateau_joueur2)
            self.choose_starter()
            self.play(self.conf.config)
        elif self.conf.mode == 3:
            # Initialisation du joueur1
            self.joueur1 = PlayerIA(self.conf, plateau_joueur1)
            self.joueur1.start = True
            # Sauvegarde des paramètres qui se retrouve lors des parties suivantes
            joueur1_init = [self.joueur1.name, self.joueur1.IA.difficulte]
            # Initialisation du joueur2
            self.joueur2 = PlayerIA(self.conf, plateau_joueur2)
            # Sauvegarde des paramètres qui se retrouve lors des parties suivantes
            joueur2_init = [self.joueur2.name, self.joueur2.IA.difficulte]
            # Choix du nombre de parties
            if args.play_number is not None and args.play_number <= 0:
                parser.error("L'argument play_number doit être positif.")
            numb = args.play_number
            if numb is None:
                numb = Battleship.choose_number_plays()
            # Boucle définissant le nombre de parties à effectuer
            for i in range(numb):
                print(i)
                plateau_joueur1 = Plateau(self.conf.config)
                plateau_joueur2 = Plateau(self.conf.config)
                self.joueur1 = PlayerIA(self.conf, plateau_joueur1, init=joueur1_init)
                self.joueur1.start = True
                self.joueur2 = PlayerIA(self.conf, plateau_joueur2, init=joueur2_init)  
                self.play(self.conf.config, auto_IA=True)

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
            
        .. seealso:: choose_starter_input().
        """

        start = Battleship.choose_starter_input()

        if start == '1':
            self.joueur1.start = True
            print("{joueur1} commence la partie.".format(joueur1=self.joueur1.name))
        elif start == '2':
            self.joueur2.start = True
            print("{joueur2} commence la partie.".format(joueur2=self.joueur2.name))
            
    @classmethod
    @while_true
    def choose_starter_input(cls):
        """Input de qui commence.
        
        Returns:
            start (int): Joueur 1, 2 ou aléatoire.
        """
        
        start = input(
            "Choisissez qui commence la partie (1, 2, A): ")
        if not start in ['1', '2', 'A']:
            raise ValueError("Entrer 1, 2 ou A.")
        if start == 'A':
            start = secrets.choice(['1', '2'])
        return start
    
    @timethis
    def play(self, config, auto_IA = False):
        """Jeu tour par tour.

        Args:
            self.joueur1 (class instance): Instance de la classe Player() du joueur 1.
            self.joueur2 (class instance): Instance de la classe Player() du joueur 2.
            self.aleatoire (boolean): Si le placement est aléatoire (IA) ou non (player).
            auto_IA (boolean): Partie IA vs IA automatique.

        Raises:
            ValueError: Un tir à déjà été effectué sur cette position.

        .. seealso:: altern_player(), choose_position(), affichage_our_ships(), affichage_our_tir(), cases_possibles(), boat_sink().
        """

        # Création de la liste contenant les deux joueurs
        altern_joueur = self.altern_player()

        # Boucle globale du jeu
        n = 0 # Compteur pour alterner les joueurs
        fin_partie = False # Variable de fin de partie
        while not fin_partie:
            # Boucle qui gère les exceptions de l'input
            while not fin_partie:
                try:
                    print("Au tour de {nom_joueur}.".format(nom_joueur=altern_joueur[n % 2].name))
                    # Choix de l'emplacement du tir
                    position = self.choose_position(auto_IA, altern_joueur, n)
                    # Parcours du plateau
                    for i in range(config["columns"] * config["lines"]):
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
                    print(altern_joueur[n % 2])
                    # Affichage du plateau
                    altern_joueur[n % 2].plateau.affichage_our_ships(config)
                    altern_joueur[n % 2].plateau.affichage_our_tir(config)
                    # Regarde les possibilités de tir
                    altern_joueur[n % 2].IA.cases_possibles(altern_joueur[(n + 1) % 2], altern_joueur[n % 2])
                    # Regarde si un bateau est coulé
                    altern_joueur[n % 2].IA.boat_sink(altern_joueur[(n + 1) % 2], altern_joueur[n % 2])
                    if altern_joueur[(n + 1)% 2].ships_left == 0:
                        fin_partie = True
                    break
                except ValueError as VE:
                    print(VE)
            n += 1
        print("La partie est terminée.\n{gagnant} a gagné !!!".format(gagnant=altern_joueur[(n + 1) % 2].name))
        print(altern_joueur[(n + 1) % 2])

    def altern_player(self):
        """Mise en place du joueur qui commence la partie.

        Returns:
            altern_joueur (list): 2 joueurs dans une liste.
        """

        if self.joueur1.start == True:
            first = self.joueur1
            second = self.joueur2
        elif self.joueur2.start == True:
            first = self.joueur2
            second = self.joueur1

        return [first, second]

    def choose_position(self, auto_IA, altern_joueur, n):
        """Choix de la position en fonction du joueur actuel.
         - IA vs IA
         - IA
         - Joueur

        Args:
            auto_IA (boolean): Partie IA vs IA automatique.
            altern_joueur (list):

        Returns:
            position (str): Coordonnées de la case choisie.

        Raises:
            ValueError : La case n'appartient pas au plateau.

        .. seealso:: play_ia(), exec_strategie().
        """

        if auto_IA == True: # IA vs IA
            position = self.play_ia(n, altern_joueur)
        elif self.joueur2.aleatoire == True and n % 2 == altern_joueur.index(self.joueur2): # Joueur vs IA
            position = self.joueur2.IA.exec_strategie(self.joueur1, self.joueur2, self.conf.config)
        else: # Joueur
            position = input("Entrer la case cible de votre tir : ")
            if not position in Plateau.table:
                raise ValueError(
                    "Entrer une case qui est présente sur le plateau.")
        return position

    def play_ia(self, n, altern_joueur):
        """Exécution de la stratégie de l'IA 1 ou de l'IA 2.

        Returns:
            position (str): Coordonnées de la case choisie.

        .. seealso:: exec_strategie().
        """

        if n % 2 == altern_joueur.index(self.joueur2):
            position = self.joueur2.IA.exec_strategie(self.joueur1, self.joueur2, self.conf.config)
        elif n % 2 == altern_joueur.index(self.joueur1):
            position = self.joueur1.IA.exec_strategie(self.joueur2, self.joueur1, self.conf.config)

        return position
    
    @classmethod
    @while_true
    def choose_number_plays(cls):
        """Input du nombre de parties (IA vs IA).
        
        Returns:
            numb (int): Nombre de parties.
        """
        
        numb = int(input(
            "\nChoisissez le nombre de parties à effectuer: "))
        if numb <= 0:
            raise ValueError("Entrer un nombre positif.")
        return numb

    def __str__(self):
        """Affichage de tous les attributs de la classe.

        Returns:
            self.joueur1 (class instance): Instance de la classe Player() du joueur 1.
            self.joueur2 (class instance): Instance de la classe Player() du joueur 2.
            self.conf (class instance): Instance de la classe Configuration().
        """

        return "Configuration : {},\nJoueur 1 : {},\nJoueur 2 : {}\n".format(self.conf, self.joueur1, self.joueur2)

def main():
    """Routine globale.
    
    .. seealso:: get_parser(), Battleship().
    """

    # Initialisation du parser
    args, parser = get_parser()
    # Lancement du programme
    Battleship(args, parser)

def get_parser():
    """Création du parser et de tous ses arguments.
    
    Returns:
        args (class instance): Argument entrés en ligne de commande.
        parser (class instance): Parser de la ligne de commande.
        
    Raises:
        parser.error: Erreurs des inputs sur le cmd.
    """

    # Initialisation du parser
    parser = argparse.ArgumentParser(prog='Battleship', description='Jeu de bataille navale')
    parser.add_argument('--version', action='version', version='%(prog)s 1.3.0')
    
    # Sub-parser new_config
    subparsers = parser.add_subparsers()
    new_config = subparsers.add_parser('new-config', help='Création d\'une nouvelle configuration. Entrer le nombre de colonnes, suivi du nombre de ligne et de la liste des bateaux.')
    new_config.add_argument('-c', '--columns', help='Nombre de colonnes.', type=int, metavar='N', default=None, dest='columns', required=True)
    new_config.add_argument('-l', '--lines', help='Nombre de lignes.', type=int, metavar='N', default=None, dest='lines', required=True)
    new_config.add_argument('-b', '--boats', help='Nombres de bateaux de tailles 2,3,4 et 5 séparés par une virgule.', type=str, metavar='N',
                            default=None, dest='boat', required=True)

    parser.add_argument('-ec', '--exist-config', help='Choix d\'une configuration existante dans la liste des configurations. Entrer la ligne voulue.',
                            default=None, metavar='ligne', type=int, dest='exist_config')
    parser.add_argument('-cf', '--conf-file', help='Fichier contenant les configurations.',
                            metavar='filename', default=None, dest='file_name', type=str)
    parser.add_argument('-m', '--mode', help='Mode de jeu. 1. PVP/ 2. PVE/ 3. IA vs IA.', type=int, choices=[1, 2, 3],
                            metavar='mode', default=None, dest='mode')
    parser.add_argument('-n', '--number', help='Nombre de parties IA vs IA.', type=int, metavar='N', default=None, dest='play_number')
    # Appel de la fonction qui cré les commandes
    args = parser.parse_args()
    # Gestion des commandes exclusives
    if hasattr(args, 'columns') and args.exist_config is not None and ((args.columns and args.lines and args.boat) is not None):
        # Sans appel de new-config, args ne cré pas les attributs du subparser
        parser.error('Les arguments exist_config et new_config ne sont pas compatibles.')
    if args.play_number is not None and args.mode != 3:
        parser.error("L'argument play_number nécessite l'argument mode égal à 3.")

    return args, parser

if __name__ == '__main__':
    sys.exit(main())
