#DISCLAIMER: Digital assets and images were found on http://pixelartmaker.com/art/770b2d9c0cd84bf. This project is meant for educational purposes only.


#These are our imports. I use random to generate random values for damage calculation as well as drawing Pokemon. Pycodestyle is something I haven't quite figured out /
#how to enable yet, pygame is the module that I will be using to represent the game. Sys is used to safely exit the game loop without crashing. I wound up using /
#Numpy as it had a very specifc method that I liked in choosing a number with weights. Time is pretty self explanatory; I want to be able to add delays. / 
#String and digits is used to handle unique pokemon names to strip extra numbers and be able to recognize the original pokemon name. Math is pretty handy for damage!
import random
import pycodestyle
import pygame
import sys 
import numpy
import time
from string import digits
import math
import os


#First I start by defining Player_turn and EN_turn, each assigned a value. This binary-type system will alternate either between player and computer turns. I by default /
#Set it to the player turn.
PLAYER_TURN, EN_TURN = 0, 1
state = PLAYER_TURN


class pygput:
    '''This class takes in a screen display destination, a string to be displayed, a location where on the screen, the font type, and the class reference and acts like input() on the terminal, but for pygame.
    Additionally, it determines whether the pokedex_class has been inputted (and therefore the battle has begun) and appropriately displays the Pokemon in battle. Also, if the
    game_ref.number, which is the SCENE index, is at 0, that means the game just started and it displays the title screen. SCREEN represents the surface where everything gets
    displayed. I tried to make the blit text as smart as possible so that it would start a new line if it detects an excessively long string that is too large for the width
    of the screen.'''


    def __init__(self, SCREEN, STRING, LOCATION, FONT, REF, game_ref, pokedex_class = None):
        self.STRING = STRING
        work_dir = os.path.dirname(os.path.abspath(__file__))
        if game_ref.number == 0:
            Bkg = pygame.image.load(f'{work_dir}/Assets/IMG.jpg')
            Bkg = pygame.transform.scale(Bkg, (1024, 720))
            Ttl = pygame.image.load(f'{work_dir}/Assets/Logo.png')
            Ttl = pygame.transform.scale(Ttl, (500, 200))
            SCREEN.blit(Bkg, (0,0))
            SCREEN.blit(Ttl, (262,260))
        elif pokedex_class != None:
            Bkg = pygame.image.load(f'{work_dir}/Assets/Background.jpg')
            Bkg = pygame.transform.scale(Bkg, (1024, 720))
            SCREEN.blit(Bkg, (0,0))
            PkEnemyImg = pygame.image.load(f'{work_dir}/Assets/{pokedex_class.OPPONENT}.png')
            PkPlayerImg = pygame.image.load(f'{work_dir}/Assets/{pokedex_class.BATTLER}.png')
            PkEnemyImg = pygame.transform.scale(PkEnemyImg, (200, 200))
            PkPlayerImg = pygame.transform.scale(PkPlayerImg, (200, 200))
            SCREEN.blit(PkEnemyImg, (254, 190))
            SCREEN.blit(PkPlayerImg, (584, 190))
        else:
            Bkg = pygame.image.load(f'{work_dir}/Assets/Background.jpg')
            Bkg = pygame.transform.scale(Bkg, (1024, 720))
            SCREEN.blit(Bkg, (0,0))
        str_list = []
        x = 0
        if len(self.STRING) >= 120:
            str_list = [self.STRING[i:i+120] for i in range(0, len(self.STRING), 120)]
            for string in str_list:
                x += 20
                string_sf = FONT.render(string, 0, pygame.Color('white'))
                SCREEN.blit(string_sf, (10, x))
        elif len(self.STRING) < 120:
            string_sf = FONT.render(self.STRING, 0, pygame.Color('white'))
            SCREEN.blit(string_sf, (10, 10))


class CallableDictionary(dict):
    '''#CREDIT TO https://stackoverflow.com/questions/46106779/dictionary-value-as-function-to-be-called-when-key-is-accessed-without-using. This takes a dictionary like
    variable and if you refer to the key, it works by executing the given value. I can therefore jump between game scenes in a convenient matter by simply reffering to
    the key'''
    def __getitem__(self, key):
        value = super().__getitem__(key)
        if callable(value):
            return value()
        return value


#In this game's code, I will continually reference things like ref and ref2. Just know that these attributes represent a certain class instance.


class Pokemon():
    '''This is my Pokemon class. This class is useful for calculating damage based on the pokemon attributes which are shown below.'''


    def __init__(self, name, type_, HP, Attack, Defense, Speed, Experience, Moves, Level, ref):
        '''Sets inputted variables to self for access in all methods in this class. Ref will refer to our pokedex class instance while ref2 will refer to our game class instance'''
        self.name = name
        self.type_ = type_
        self.HP = HP
        self.starter_HP = HP
        self.Attack = Attack
        self.Defense = Defense
        self.Speed = Speed
        self.Experience = Experience
        self.Moves = Moves
        self.ref = ref


    def calculate_damage(self, attack_pokemon, defense_pokemon, selected_move, inst2, game_ref): 
        '''This calculates damage for pokemon using a target, some other class references, and the attacker, using our already defined attributes.'''
        random_ = random.randint(85,101)/100
        speed = self.Speed
        experience = self.Experience
        power = self.ref.MOVES_DICTIONARY[selected_move]["power"]
        attack = self.Attack
        defense = self.Defense
        critical = numpy.random.choice([1, 2], p = [(1-(speed/512)), speed/512])
        x = 1
        if len(self.ref.CHARACTERS[defense_pokemon]['Type']) == 1:
            if any(self.ref.CHARACTERS[defense_pokemon]['Type'] == weakness for weakness in self.ref.MOVES_DICTIONARY[selected_move]['not very effective against']):
                x = x*(1/2)
            elif any(self.ref.CHARACTERS[defense_pokemon]['Type'] == advantage for advantage in self.ref.MOVES_DICTIONARY[selected_move]['super effective against']):
                x = x*2
            else:
                x = x
        elif len(self.ref.CHARACTERS[defense_pokemon]['Type']) > 1:
            types = self.ref.CHARACTERS[defense_pokemon]['Type']
            for type_ in types:
                if any(type_ == weakness for weakness in self.ref.MOVES_DICTIONARY[selected_move]['not very effective against']):
                    x = x*(1/2)
                elif any(type_ == advantage for advantage in self.ref.MOVES_DICTIONARY[selected_move]['super effective against']):
                    x = x*2
                else:
                    x = x
        atck_type = x
        modifier = critical * random_ * atck_type 
        damage = ((((2*(experience**(1/3))/5)+2)*power*(attack/defense))/50)*modifier
        return damage


class battle_mainclass:
    '''This battle_mainclass is a class rather than a method of pokemon. I figured it would be more fitting to make it create each two pokemon classes. it also helps
    in alternating between player and enemy turns.'''


    def create_class(self, screen, font, ref, game_ref):
        self.screen = screen
        self.ENEMY = Pokemon(ref.OPPONENT, ref.CHARACTERS[ref.OPPONENT]['Type'], 
                        ref.CHARACTERS[ref.OPPONENT]['HP'], ref.CHARACTERS[ref.OPPONENT]['Attack'], 
                        ref.CHARACTERS[ref.OPPONENT]['Defense'], ref.CHARACTERS[ref.OPPONENT]['Speed'], 
                        ref.CHARACTERS[ref.OPPONENT]['Experience'], ref.CHARACTERS[ref.OPPONENT]['Moves'], 
                        Level = None, ref = ref)
        if ref.BATTLER not in ['Charmander', 'Squirtle', 'Bulbasaur']:
            self.PLAYER = Pokemon(ref.BATTLER,
                            ref.CHARACTERS[ref.BATTLER]['Type'], 
                            ref.CHARACTERS[ref.BATTLER]['HP'], ref.CHARACTERS[ref.BATTLER]['Attack'], 
                            ref.CHARACTERS[(ref.BATTLER)]['Defense'], ref.CHARACTERS[ref.BATTLER]['Speed'], 
                            ref.CHARACTERS[(ref.BATTLER)]['Experience'], ref.CHARACTERS[ref.BATTLER]['Moves'], 
                            Level = None, ref = ref)
        else:
            self.PLAYER = Pokemon(ref.BATTLER,
                            ref.CHARACTERS[ref.BATTLER]['Type'], 
                            ref.CHARACTERS[ref.BATTLER]['HP'], ref.CHARACTERS[ref.BATTLER]['Attack'], 
                            ref.CHARACTERS[(ref.BATTLER)]['Defense'], ref.CHARACTERS[ref.BATTLER]['Speed'], 
                            ref.pokedex[(ref.NAME)]['Experience'], ref.CHARACTERS[ref.BATTLER]['Moves'], 
                            Level = None, ref = ref)
        global state
        global result
        if ref.CHARACTERS[ref.BATTLER]['Speed'] > ref.CHARACTERS[ref.OPPONENT]['Speed']:
            state = PLAYER_TURN
        elif ref.CHARACTERS[ref.BATTLER]['Speed'] < ref.CHARACTERS[ref.OPPONENT]['Speed']:
            state = EN_TURN
        else:
            state = PLAYER_TURN
        game_ref.number += 1


class turn:
    '''Turn is a class refering to player and AI turns by detecting some attributes from the battle_mainclass'''


    def pick(self, font, screen, game_ref, pokedex_class, main_class):
        '''This method evalutes that players damage after their turn since the player turn is continually checking in the loop for player inputs.
        Otherwise, my player class would infinitely subtract damage from the opponent if not executed in here. This has to do with callable dictionary
        properties where I try to distinguish one time events for calculations and looping for graphics and text inputs. It also works y resetting the SCENES dictionary
        back to the original to restart the battles and allow the game to theoretically go to infinity. it checks for health and if the player wins, it moves on to the
        next scene, by changing game_ref.number. If the binary-esque state = 1 or 0 (player_turn or en_turn) it runs the corresponding AI or player turn'''
        global state
        try:
            main_class.ENEMY.HP -= self.dmg1
        except:
            None
        if main_class.ENEMY.HP <= 0:
            time.sleep(2)
            state = None
            self.n = 1
            if f"{pokedex_class.OPPONENT}{self.n}" in pokedex_class.pokedex.keys():
                self.n += 1
            pokedex_class.pokedex[f"{(pokedex_class.OPPONENT)}{self.n}"] = pokedex_class.CHARACTERS.get(pokedex_class.OPPONENT)
            pokedex_class.pokedex[pokedex_class.NAME]['Experience'] = pokedex_class.CHARACTERS[pokedex_class.OPPONENT].get('Experience')
            self.SCENES = CallableDictionary({
                0: lambda: player.game_start(screen, font, ref = self, ref2 = self),
                1: lambda: player.choose_fight(screen, font, ref = player, ref2 = self),
                2: lambda: mainclass.create_class(screen, font, ref = player, game_ref = self),
                3: lambda: self.turn.pick(font, screen, self, player, mainclass),
                -1: lambda: game_over()
            })
            game_ref.run_inst = set([0])
            game_ref.number = 1
        if state == PLAYER_TURN:
            self.dmg_dict = {}
            moves = pokedex_class.CHARACTERS[pokedex_class.BATTLER]['Moves']
            for move in moves:
                self.dmg_dict[move] = main_class.PLAYER.calculate_damage(str(pokedex_class.BATTLER), str(pokedex_class.OPPONENT), move, main_class.ENEMY, game_ref)
            game_ref.pyinput_text = None
            game_ref.SCENES[game_ref.number+1] = lambda: self.PL(font, screen, game_ref, pokedex_class, main_class)
            game_ref.TEXT_DISPLAYS[game_ref.number+1] = lambda: conditional_turn_display(font, screen, game_ref, pokedex_class, main_class)
            game_ref.number += 1
        if state == EN_TURN:
            self.AI(font, screen, game_ref, pokedex_class, main_class)


    def AI(self, font, screen, game_ref, pokedex_class, main_class):
        '''AI randomly choses from a pokemons available moves based on the pokedex CHARACTERS. It deals with damage within the method as it does not need to iterate
        multiple times. It also handles the event for if the player loses and simply removes a pokemon, or if the player has no pokemon left and sets it to the last scene'''
        global state
        time.sleep(2)
        moves = pokedex_class.CHARACTERS[pokedex_class.BATTLER]['Moves']
        move = numpy.random.choice(moves)
        print(move)
        self.dmg2 = main_class.ENEMY.calculate_damage(str(pokedex_class.OPPONENT), str(pokedex_class.BATTLER), move, main_class.PLAYER, game_ref)
        state = PLAYER_TURN
        main_class.PLAYER.HP -= self.dmg2
        if main_class.PLAYER.HP <= 0:
            state = None
            pokedex_class.pokedex.pop(str(pokedex_class.NAME))
            if len(pokedex_class.pokedex) < 1:
                game_ref.number = -1
            else:
                self.SCENES = CallableDictionary({
                0: lambda: player.game_start(screen, font, ref = self, ref2 = self),
                1: lambda: player.choose_fight(screen, font, ref = player, ref2 = self),
                2: lambda: mainclass.create_class(screen, font, ref = player, game_ref = self),
                3: lambda: self.turn.pick(font, screen, self, player, mainclass),
                -1: lambda: game_over()
                })
                game_ref.run_inst = set([0])
                game_ref.number = 1
        if game_ref.number != -1 and game_ref.number != 1:
            game_ref.SCENES[game_ref.number+1] = lambda: game_ref.turn.pick(font, screen, game_ref, pokedex_class, main_class)
            game_ref.TEXT_DISPLAYS[game_ref.number+1] = lambda: conditional_turn_display(font, screen, game_ref, pokedex_class, main_class)
            game_ref.number += 1


    def PL(self, font, screen, game_ref, pokedex_class, main_class):
        '''this player turn continually runs in the while loop of pygame in order to detect text input of the user and match it with the corresponding damage. It can also update
        the scene to the next.'''
        global state
        for key, value in self.dmg_dict.items():
            if key == game_ref.pyinput_text:
                self.dmg1 = value
                state = EN_TURN
                game_ref.SCENES[game_ref.number+1] = lambda: game_ref.turn.pick(font, screen, game_ref, pokedex_class, main_class)
                game_ref.TEXT_DISPLAYS[game_ref.number+1] = lambda: conditional_turn_display(font, screen, game_ref, pokedex_class, main_class)
                game_ref.number += 1


class conditional_turn_display:
    '''this class determines what text and imagse should be displayed to the user using our custom pygput class. It handles turns, losses, wins, etc... using
    the state for player_turn and en_turn, as well as if hp is less than 0 and if there are no more pokemon (as well as if there still are)'''


    def __init__(self, font, screen, game_ref, pokedex_class, main_class):
        global state
        if state == PLAYER_TURN:
            pygput(screen, f'PLAYER HP: {math.ceil(main_class.PLAYER.HP)} | ENEMY HP: {math.ceil(main_class.ENEMY.HP)} | TYPE YOUR MOVE {main_class.PLAYER.Moves}', (10,12), font, self,game_ref, pokedex_class)
        elif state == EN_TURN:
            pygput(screen, f'PLAYER HP: {math.ceil(main_class.PLAYER.HP)} | ENEMY HP: {math.ceil(main_class.ENEMY.HP)} | ENEMY IS MAKING A MOVE...', (10,12), font, self, game_ref, pokedex_class)
        elif game_ref.number == -1:
            pygput(screen, 'Your last Pokemon has fainted....GAME OVER......', (10,12), font, self, game_ref)
        elif main_class.PLAYER.HP <= 0 and len(pokedex_class.pokedex) > 1:
            pygput(screen, 'Your Pokemon has fainted...Pokemon no longer in your Pokedex...', (10,12), font, self, game_ref)
        elif main_class.ENEMY.HP <= 0:
            pygput(screen, 'VICTORY: OPPONENT HAS FAINTED...ADDING POKEMON TO YOUR POKEDEX...', (10,12), font, self, game_ref)


class pokedex:
    '''this is our pokedex class. It acts like a blackjack hand as well as a library we can continually refer to when we want to know certain pokemon traits
    when handling the battles. We can add pokemon and remove them from the hand (although it is not its own method)'''


    def __init__(self):
        self.pokedex = {}
        self.MOVES_DICTIONARY = {
    'Scratch': 
    {
        'name': 'Scratch',
        'power': 40, 
        'type': 'Normal', 
        'super effective against': ['N/A'], 
        'not very effective against': ['Rock', 'Steel']
    }, 
    'Tackle': 
    {
        'name': 'Tackle',
        'power': 40, 
        'type': 'Normal', 
        'super effective against': ['N/A'], 
        'not very effective against': ['Rock', 'Steel']
    }, 
    'Pound': {'name': 'Pound', 'power': 40, 'type': 'Normal', 'super effective against': ['N/A'], 'not very effective against': ['Rock', 'Steel']}, 
    'Rage': {'name': 'Rage', 'power': 20, 'type': 'Normal', 'super effective against': ['N/A'], 'not very effective against': ['Rock', 'Steel']}, 
    'Fury Attack': {'name': 'Fury Attack', 'power': 15, 'type': 'Normal', 'super effective against': ['N/A'], 'not very effective against': ['Rock', 'Steel']}, 
    'Ember': {'name': 'Ember', 'power': 40, 'type': 'Fire', 'super effective against': ['Grass', 'Ice', 'Bug', 'Steel'], 'not very effective against': ['Fire', 'Water', 'Rock', 'Dragon']}, 
    'Fire Spin': {'name': 'Fire Spin', 'power': 35, 'type': 'Fire', 'super effective against': ['Grass', 'Ice', 'Bug', 'Steel'], 'not very effective against': ['Fire', 'Water', 'Rock', 'Dragon']}, 
    'Bubble': {'name': 'Bubble', 'power': 40, 'type': 'Water', 'super effective against': ['Fire', 'Ground', 'Rock'], 'not very effective against': ['Water', 'Grass', 'Dragon']}, 
    'Aqua Jet': {'name': 'Aqua Jet', 'power': 40, 'type': 'Water', 'super effective against': ['Fire', 'Ground', 'Rock'], 'not very effective against': ['Water', 'Grass', 'Dragon']}, 
    'Thunder Shock': {'name': 'Thunder Shock', 'power': 40, 'type': 'Electric', 'super effective against': ['Water', 'Flying'], 'not very effective against': ['Electric', 'Grass', 'Dragon']}, 
    'Thunderbolt': {'name': 'Thunderbolt', 'power': 90, 'type': 'Electric', 'super effective against': ['Water', 'Flying'], 'not very effective against': ['Electric', 'Grass', 'Dragon']}, 
    'Vine Whip': {'name': 'Vine Whip', 'power': 45, 'type': 'Grass', 'super effective against': ['Water', 'Ground', 'Rock'], 'not very effective against': ['Fire', 'Grass', 'Poison', 'Flying', 'Bug', 'Dragon', 'Steel']}, 
    'Magical Leaf': {'name': 'Magical Leaf', 'power': 60, 'type': 'Grass', 'super effective against': ['Water', 'Ground', 'Rock'], 'not very effective against': ['Fire', 'Grass', 'Poison', 'Flying', 'Bug', 'Dragon', 'Steel']}, 
    'Ice Shard': {'name': 'Ice Shard', 'power': 40, 'type': 'Ice', 'super effective against': ['Grass', 'Ground', 'Flying', 'Dragon'], 'not very effective against': ['Fire', 'Water', 'Ice', 'Steel']}, 
    'Double Kick': {'name': 'Double Kick', 'power': 30, 'type': 'Fighting', 'super effective against': ['Normal', 'Ice', 'Rock', 'Dark', 'Steel'], 'not very effective against': ['Poison', 'Flying', 'Psychic', 'Bug', 'Fairy']}, 
    'Earthquake': {'name': 'Earthquake', 'power': 100, 'type': 'Ground', 'super effective against': ['Fire', 'Electric', 'Poison', 'Rock', 'Steel'], 'not very effective against': ['Grass', 'Bug']}, 
    'Wing Attack': {'name': 'Wing Attack', 'power': 60, 'type': 'Flying', 'super effective against': ['Grass', 'Fighting', 'Bug'], 'not very effective against': ['Electric', 'Rock', 'Steel']}, 
    'Peck': {'name': 'Peck', 'power': 35, 'type': 'Flying', 'super effective against': ['Grass', 'Fighting', 'Bug'], 'not very effective against': ['Electric', 'Rock', 'Steel']}, 
    'Confusion': {'name': 'Confusion', 'power': 50, 'type': 'Psychic', 'super effective against': ['Fighting', 'Poison'], 'not very effective against': ['Psychic', 'Steel']}, 
    'Twineedle': {'name': 'Twineedle', 'power': 25, 'type': 'Bug', 'super effective against': ['Grass', 'Psychic', 'Dark'], 'not very effective against': ['Fire', 'Fighting', 'Poison', 'Flying', 'Ghost', 'Steel', 'Fairy']}, 
    'Rock Throw': {'name': 'Rock Throw', 'power': 50, 'type': 'Rock', 'super effective against': ['Fire', 'Ice', 'Flying', 'Bug'], 'not very effective against': ['Fighting', 'Ground', 'Steel']}, 
    'Rock Slide': {'name': 'Rock Slide', 'power': 75, 'type': 'Rock', 'super effective against': ['Fire', 'Ice', 'Flying', 'Bug'], 'not very effective against': ['Fighting', 'Ground', 'Steel']}, 
    'Lick': {'name': 'Lick', 'power': 30, 'type': 'Ghost', 'super effective against': ['Psychic', 'Ghost'], 'not very effective against': ['Dark']}, 
    'Outrage': {'name': 'Outrage', 'power': 120, 'type': 'Dragon', 'super effective against': ['Dragon'], 'not very effective against': ['Steel']}, 
    'Crunch': {'name': 'Crunch', 'power': 80, 'type': 'Dark', 'super effective against': ['Psychic', 'Ghost'], 'not very effective against': ['Fighting', 'Dark', 'Fairy']}, 
    'Bite': {'name': 'Bite', 'power': 60, 'type': 'Dark', 'super effective against': ['Psychic', 'Ghost'], 'not very effective against': ['Fighting', 'Dark', 'Fairy']}, 
    'Flash Cannon': {'name': 'Flash Cannon', 'power': 80, 'type': 'Steel', 'super effective against': ['Ice', 'Rock', 'Fairy'], 'not very effective against': ['Fire', 'Water', 'Electric', 'Steel']}, 
    'Smog': {'name': 'Smog', 'power': 30, 'type': 'Poison', 'super effective against': ['Grass', 'Fairy'], 'not very effective against': ['Poison', 'Ground', 'Rock', 'Ghost']}, 
    'Dream Eater': {'name': 'Dream Eater', 'power': 100, 'type': 'Psychic', 'super effective against': ['Fighting', 'Poison'], 'not very effective against': ['Psychic', 'Steel']}, 
    'Body Slam': {'name': 'Body Slam', 'power': 85, 'type': 'Normal', 'super effective against': ['N/A'], 'not very effective against': ['Rock', 'Steel']}, 
    'Double Slap': {'name': 'Double Slap', 'power': 15, 'type': 'Normal', 'super effective against': ['N/A'], 'not very effective against': ['Rock', 'Steel']}, 
    'Razor Leaf': {'name': 'Razor Leaf', 'power': 55, 'type': 'Grass', 'super effective against': ['Water', 'Ground', 'Rock'], 'not very effective against': ['Fire', 'Grass', 'Poison', 'Flying', 'Bug', 'Dragon', 'Steel']}, 
    'Headbutt': {'name': 'Headbutt', 'power': 70, 'type': 'Normal', 'super effective against': ['N/A'], 'not very effective against': ['Rock', 'Steel']}, 
    'Absorb': {'name': 'Absorb', 'power': 20, 'type': 'Grass', 'super effective against': ['Water', 'Ground', 'Rock'], 'not very effective against': ['Fire', 'Grass', 'Poison', 'Flying', 'Bug', 'Dragon', 'Steel']}, 
    'Fairy Wind': {'name': 'Fairy Wind', 'power': 40, 'type': 'Fairy', 'super effective against': ['Fighting', 'Dragon', 'Dark'], 'not very effective against': ['Fire', 'Poison', 'Steel']}, 
    'Struggle Bug': {'name': 'Struggle Bug', 'power': 50, 'type': 'Bug', 'super effective against': ['Grass', 'Psychic', 'Dark'], 'not very effective against': ['Fire', 'Fighting', 'Poison', 'Flying', 'Ghost', 'Steel', 'Fairy']}, 
    'Draining Kiss': {'name': 'Draining Kiss', 'power': 50, 'type': 'Fairy', 'super effective against': ['Fighting', 'Dragon', 'Dark'], 'not very effective against': ['Fire', 'Poison', 'Steel']}, 
    'Shadow Ball': {'name': 'Shadow Ball', 'power': 80, 'type': 'Ghost', 'super effective against': ['Psychic', 'Ghost'], 'not very effective against': ['Dark']}
}
        self.MOVES = {
    "Normal" : [ 'Scratch', 'Tackle',  'Pound', 'Rage', 'Fury Attack', 'Body Slam', 'Double Slap', 'Headbutt'] ,
    "Fire" : ['Ember', 'Fire Spin'],
    "Water" : ['Bubble', 'Aqua Jet'],
    "Electric" : ['Thunder Shock', 'Thunderbolt'],
    "Grass" : ['Vine Whip', 'Magical Leaf', 'Razor Leaf', 'Absorb'],
    "Ice" : ['Ice Shard'],
    "Fighting" : ['Double Kick'],
    "Poison" : ['Smog'],
    "Ground" : ['Earthquake'],
    "Flying" : ['Wing Attack', 'Peck'],
    "Psychic" : ['Confusion', 'Dream Eater'] ,
    "Bug" : ['Twineedle', 'Struggle Bug'],
    "Rock" : ['Rock Throw', 'Rock Slide'],
    "Ghost" : ['Lick', 'Shadow Ball'] ,
    "Dragon" : ['Outrage'],
    "Dark" : ['Crunch', 'Bite'],
    "Steel" : ['Flash Cannon'],
    "Fairy" : ['Fairy Wind', 'Draining Kiss']
    }
        self.CHARACTERS = {
    'Pikachu': {'Type': ['Electric'], 'HP': 35, 'Moves': ['Thunder Shock',  'Double Kick', 'Thunderbolt'], 'Attack': 55, 'Defense': 40, 'Speed': 90, 'Experience': 112},
    'Charizard': {'Type': ['Fire', 'Flying'], 'HP': 78, 'Moves': [ 'Crunch', 'Ember', 'Scratch', 'Wing Attack'], 'Attack': 84, 'Defense': 78, 'Speed': 100, 'Experience': 240},
    'Squirtle': {'Type': ['Water'], 'HP': 44, 'Moves': ['Tackle',  'Bubble', 'Bite'], 'Attack': 48, 'Defense': 65, 'Speed': 43, 'Experience': 63},
    'Jigglypuff': {'Type': ['Normal', 'Fairy'], 'HP': 115, 'Moves': ['Pound', 'Body Slam', 'Double Slap'], 'Attack': 45, 'Defense': 20, 'Speed': 20, 'Experience': 95},
    'Gengar': {'Type': ['Ghost', 'Poison'], 'HP': 60, 'Moves': ['Lick', 'Smog', 'Dream Eater', 'Shadow Ball'], 'Attack': 65, 'Defense': 60, 'Speed': 110, 'Experience':225},
    'Magnemite': {'Type': ['Electric', 'Steel'], 'HP': 25, 'Moves': [ 'Tackle', 'Flash Cannon', 'Thunder Shock', 'Thunderbolt'],  'Attack': 35, 'Defense': 70, 'Speed': 45, 'Experience': 65},
    'Bulbasaur': {'Type': ['Grass', 'Poison'], 'HP': 45, 'Moves': ['Tackle', 'Vine Whip', 'Razor Leaf'], 'Attack': 49, 'Defense': 49, 'Speed': 45, 'Experience': 64},
    'Charmander': {'Type': ['Fire'], 'HP': 39, 'Moves': ['Scratch', 'Ember', 'Fire Spin'], 'Attack': 52, 'Defense': 43, 'Speed': 65, 'Experience': 62},
    'Beedrill': {'Type': ['Bug', 'Poison'], 'HP': 65, 'Moves': ['Peck', 'Twineedle', 'Rage', 'Fury Attack', 'Outrage'], 'Attack': 90, 'Defense': 40, 'Speed': 75, 'Experience': 178},
    'Golem': {'Type': ['Rock', 'Ground'], 'HP': 80, 'Moves': [ 'Tackle', 'Rock Throw', 'Rock Slide', 'Earthquake'], 'Attack': 120, 'Defense': 130, 'Speed': 45, 'Experience': 223},
    'Dewgong': {'Type': ['Water', 'Ice'], 'HP': 90, 'Moves': ['Aqua Jet',  'Ice Shard', 'Headbutt'], 'Attack': 70, 'Defense': 80, 'Speed': 70, 'Experience': 166},
    'Hypno': {'Type': ['Psychic'],'HP': 85, 'Moves': ['Pound', 'Confusion', 'Dream Eater'], 'Attack': 73, 'Defense': 70, 'Speed': 67, 'Experience': 169},
    'Cleffa': {'Type': ['Fairy'], 'HP': 50, 'Moves': [ 'Pound', 'Magical Leaf'], 'Attack': 25, 'Defense': 28, 'Speed': 15, 'Experience': 44},
    'Cutiefly': {'Type': ['Fairy', 'Bug'], 'HP': 40, 'Moves': ['Absorb', 'Fairy Wind', 'Struggle Bug', 'Draining Kiss'], 'Attack': 45, 'Defense': 40, 'Speed': 84, 'Experience': 61}
}


    def game_start(self, screen, font, ref, ref2):
        '''this determines what the player wants to start with as a pokemon. If the user types A. it sets the first pokemon according to the text displayed'''
        if str(ref.pyinput_text).title() == 'A':
            name_pokemon = 'Squirtle'
            if name_pokemon not in self.pokedex.keys():
                self.pokedex[name_pokemon] = self.CHARACTERS.get("Squirtle")
                self.pokedex[name_pokemon]['Experience'] = 1
        elif str(ref.pyinput_text).title() == 'B':
            name_pokemon = 'Bulbasaur'
            if name_pokemon not in self.pokedex.keys():
                self.pokedex[name_pokemon] = self.CHARACTERS.get("Bulbasaur")
                self.pokedex[name_pokemon]['Experience'] = 1
        elif str(ref.pyinput_text).title() == 'C':
            name_pokemon = 'Charmander'
            if name_pokemon not in self.pokedex.keys():
                self.pokedex[name_pokemon] = self.CHARACTERS.get("Charmander")
                self.pokedex[name_pokemon]['Experience'] = 1
        if len(self.pokedex) > 0:
            ref2.number += 1


    def choose_fight(self, screen, font, ref, ref2):
        '''this displays what pokemon the player is fighting before the battle and allows them to choose from their pokedex'''
        tr = str.maketrans('', '', digits)
        ref2.CHARS = ''
        if ref2.opponent == None:
            ref2.opponent = random.choice(list(ref.CHARACTERS))
        for key in ref.pokedex.keys():
            ref2.CHARS += f"{key} "
        for key, value in ref.pokedex.items():
            if ref2.pyinput_text == key:
                self.BATTLER = key
                self.NAME = self.BATTLER #saves the original name before translation
                self.BATTLER = (self.BATTLER).translate(tr)
                self.OPPONENT = ref2.opponent
                self.OPPONENT = (self.OPPONENT).translate(tr)
                ref2.number += 1
                ref2.opponent = None
        n = 0


def game_over():
    '''This is a very basic and understandable function (maybe it could have gone without being a function OOPS!), that allows the player
    time to contemplate their humiliating defeat to a computer playing with random moves as opposed to a coherent strategy....'''
    time.sleep(5)


class gamepy:
    '''this is the class that contains all the information compiled and creates our while loop which runs the game. I can jump between scenes, 
    which represent the computational side of the game, whereas the displays refer to the user end of the game, showing images, instructions and text.
    the -1 key in the dictionary is reserved in the event that the player loses the game to the AI and has no pokemon left (-1 so it never accidentally gets
    called if there are too many turns). Additionally, my game loop allows for the capcity to accept text input in the same way the terminal allows the user
    to do input. If the user presses return, it returns the string they entered as an input to reference names, etc... to move on to different scenes.'''


    def __init__(self):
        pygame.init()
        text = ""
        font = pygame.font.SysFont('Arial', 18)
        SIZE = WIDTH, HEIGHT = (1024, 720)
        FPS = 30
        self.pyinput_text = None
        screen = pygame.display.set_mode(SIZE, pygame.RESIZABLE)
        clock = pygame.time.Clock()
        self.number = 0
        self.opponent = None
        player = pokedex()
        mainclass = battle_mainclass()
        self.turn = turn()
        self.run_inst = set([])
        self.CHARS = ''
        self.execute_once = [0,1,2, -1]
        global state
        #This custom dictionary class stores executable class methods or functions (or whatever ex: lambda: print('Hello world')) and executes them when their key is referenced
        self.SCENES = CallableDictionary({
            0: lambda: player.game_start(screen, font, ref = self, ref2 = self),
            1: lambda: player.choose_fight(screen, font, ref = player, ref2 = self),
            2: lambda: mainclass.create_class(screen, font, ref = player, game_ref = self),
            3: lambda: self.turn.pick(font, screen, self, player, mainclass),
            -1: lambda: game_over()
            })
        self.TEXT_DISPLAYS = CallableDictionary({
            0: lambda: pygput(screen, 'Choose your Pokemon: Type A for Squirtle, B for Bulbasaur, or C for Charmander', (10,12), font, self, self),
            1: lambda: pygput(screen, f'You encountered a wild {self.opponent}. Type a name to choose a battler: {self.CHARS}', (10,10), font, player, self),
            2: lambda: None,
            3: lambda: conditional_turn_display(font, screen, self, player, mainclass), 
            -1: lambda: conditional_turn_display(font, screen, self, player, mainclass),
            })
        while True:
            dt = clock.tick(FPS) / 1000
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.pyinput_text = text
                        text = ''
                    elif event.key == pygame.K_BACKSPACE:
                        text =  text[:-1]
                    else:
                        text += event.unicode
            screen.fill(pygame.Color('black'))
            if self.number not in self.run_inst and self.number in self.execute_once:
                self.SCENES[self.number]
                self.run_inst.add(self.number)
            else:
                self.SCENES[self.number]
            self.TEXT_DISPLAYS[self.number]
            text_surf = font.render(text, True, (255, 255, 255))
            screen.blit(text_surf, text_surf.get_rect(center = screen.get_rect(center = (50,50)).center))
            pygame.display.update()


#This creates our game instance by referring to the class
PokemonGame = gamepy()