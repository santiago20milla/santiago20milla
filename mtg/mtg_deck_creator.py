from mtgsdk import Card
from mtgsdk import Set
from mtgsdk import Type
from mtgsdk import Supertype
from mtgsdk import Subtype
from mtgsdk import Changelog
import pandas as pd
import numpy as np
import pickle

CARDS = []
COMMANDER = []
MANA_TYPES = ['W','U','B','R','G']
df = []
## Commander deck only (1 commander and only 1 card included)
class deck():
    def __init__(self, **kwargs):
        self.cards = kwargs.get("CARDS", CARDS)
        self.commander = kwargs.get("COMMANDER", COMMANDER)
        self.mana_types = kwargs.get('MANA_TYPES', MANA_TYPES)
        self.deck_df = kwargs.get('DF', df)

    def define_commander(self, name):
        '''Define a commander for your deck \n ***it has to be legendary'''
        found_cards =  Card.where(name=name).all()

        dup_card_names = [cards.name for cards in found_cards] 
        card_names = (list(dict.fromkeys(dup_card_names)))

        if len(card_names) > 1:
            print('More than a single card found, please choose between:')
            for card in card_names: 
                print(card_names.index(card), card)
            index = input()
            chosen_card = found_cards[dup_card_names.index(card_names[int(index)])]
        else:
            chosen_card = found_cards[0]
        
        print('Card selected: {}'.format(chosen_card.name))

        if any('Legendary' in s for s in chosen_card.supertypes):
            self.commander.append(chosen_card)
            self.mana_types = chosen_card.color_identity
            
        else:
            print('Card chosen not Legendary')

    
    def add_card(self, name, num_repetitions=1):
        '''Add a card to your deck by setting the name and number of repeated times you want it. It has to follow your commander colors.'''
        if set([str.lower(name)]).issubset(['island','mountain','plains','swamp','forest']):
            chosen_card = Card.where(name=name).all()[0]
            self.cards.extend(chosen_card for i in range(num_repetitions))
            return

        found_cards =  Card.where(name=name).all()

        dup_card_names = [cards.name for cards in found_cards] 
        card_names = (list(dict.fromkeys(dup_card_names)))

        if len(card_names) > 1:
            print('More than a single card found, please choose between:')
            for card in card_names: 
                print(card_names.index(card), card)
            index = input()
            chosen_card = found_cards[dup_card_names.index(card_names[int(index)])]
        else:
            chosen_card = found_cards[0]
        
        print('Card selected: {}'.format(chosen_card.name))

        if set(chosen_card.color_identity).issubset(self.mana_types):
            self.cards.extend(chosen_card for i in range(num_repetitions))
        else:
            print('Card not matching commander colors. \nOverrun? (1/0)')
            overrun = input()
            if overrun == '1':
                self.cards.extend(chosen_card for i in range(num_repetitions))

    def see_cards(self):
        '''Print list with cards in your deck'''
        for i in range(0,len(self.cards)):
            print('{}: {}, {}'.format(i, self.cards[i].name, self.cards[i].type))
        
    def remove_card(self, name='none', i=-1, how='name'):
        '''Remove a card from your deck, it can be by the name or by the position index (i)'''
        if how == 'name':
            name_list = [cards.name for cards in self.cards]
            try:
                self.cards.pop(name_list.index(name))
            except ValueError:
                pass
        elif how != 'name':
            try:
                self.cards.pop(i)
            except ValueError:
                pass

    def create_dataframe(self):
        names = []
        mana_cost = []
        cost_white = []
        cost_blue = []
        cost_black = []
        cost_red = []
        cost_green = []
        types = []
        supertypes = []
        subtypes = []
        texts = []
        power = []
        toughness = []
        
        prod_white = []
        prod_blue = []
        prod_black = []
        prod_red = []
        prod_green = []
        prod_colorless = []

        for card in self.cards:
            names.append(card.name)
            mana_cost.append(card.cmc)
            types.append(card.type)
            supertypes.append(card.supertypes)
            subtypes.append(card.subtypes)
            texts.append(card.text)

            if 'Land' not in card.type:
                cost_white.append(card.mana_cost.count('W'))
                cost_blue.append(card.mana_cost.count('U'))
                cost_black.append(card.mana_cost.count('B'))
                cost_red.append(card.mana_cost.count('R'))
                cost_green.append(card.mana_cost.count('G'))
                
                prod_white.append(np.nan)
                prod_blue.append(np.nan)
                prod_black.append(np.nan)
                prod_red.append(np.nan)
                prod_green.append(np.nan)
                prod_colorless.append(np.nan)

            else:
                cost_white.append(np.nan)
                cost_blue.append(np.nan)
                cost_black.append(np.nan)
                cost_red.append(np.nan)
                cost_green.append(np.nan)
                
                mana_prod_text = card.text.split("Add")[-1]

                prod_white.append(mana_prod_text.count("{W}"))
                prod_blue.append(mana_prod_text.count("{U}"))
                prod_black.append(mana_prod_text.count("{B}"))
                prod_red.append(mana_prod_text.count("{R}"))
                prod_green.append(mana_prod_text.count("{G}"))
                prod_colorless.append(mana_prod_text.count("{C}"))
                

            if 'Creature' in card.type:
                power.append(int(card.power))
                toughness.append(int(card.toughness))
            else:
                power.append(np.nan)
                toughness.append(np.nan)

        
        self.deck_df = pd.DataFrame({'Name':names, 
                                     'Type':types,
                                     'SuperType':supertypes,
                                     'SubType':subtypes,
                                     'ManaCost':mana_cost,
                                     'W':cost_white,
                                     'U':cost_blue,
                                     'B':cost_black,
                                     'R':cost_red,
                                     'G':cost_green,
                                     'Power':power,
                                     'Toughness':toughness,
                                     'Pool_W':prod_white,
                                     'Pool_U':prod_blue,
                                     'Pool_B':prod_black,
                                     'Pool_R':prod_red,
                                     'Pool_G':prod_green,
                                     'Pool_L':prod_colorless,
                                     'Text':texts})
        
        self.deck_df.replace(0, np.nan, inplace=True)
        self.deck_df.dropna(axis=1, how='all', inplace=True)
        self.deck_df.Type[self.deck_df.Type.str.contains('Creature')] = 'Creature'

def peek_deck(deck, verbose=False):
    print("#"*200)
    print("\nQuick Analysis of: {} Deck".format(deck.commander[0].name))
    print("\n{}\n".format(deck.commander[0].text))
    print("*"*100)

    df = deck.deck_df
    color_dict = {'W':'White', 'U':'Blue', 'B':'Black', 'R':'Red', 'G':'Green'}
    mana_dict = {'W':'Plains', 'U':'Island', 'B':'Swamp', 'R':'Mountain', 'G':'Forest'}

    print("\n\nCard Distribution:\n")

    print("Creatures: \t\t\t{}".format(len(df[df.Type.str.contains('Creature')])))
    print("Instants / Sorceries: \t\t{}".format(len(df[df.Type.isin(['Instant','Sorcery'])])))
    print("Artifacts / Enchantments: \t{}".format(len(df[df.Type.isin(['Artifact','Enchantment'])])))
    print("Planeswalkers: \t\t\t{}".format(len(df[df.Type == 'Planeswalker'])))
    print("."*50)
    print("Total without Lands: \t\t{}".format(len(df[~df.Type.str.contains('Land')])))
    print("Lands: \t\t\t\t{}".format(len(df[df.Type.str.contains('Land')])))
    print("-"*50)
    print("Total Number of Cards:   \t\t{}".format(len(df)))
    print("Nonland to Land Ratio:   \t\t{}".format(round(len(df[~df.Type.str.contains('Land')])/len(df[df.Type.str.contains('Land')]),2)))
    
    print('Average Total Mana Cost: \t{}\n'.format(round(df.ManaCost.mean(),2)))
    print('\nColor Distribution: ')

    for color in deck.mana_types:
        print('\nAvg {} Mana Cost: \t\t{}'.format(color_dict[color], round(df[color].sum()/len(df[df[color] > 0]),2)))
        print('Total {} Mana Cost: \t\t{}'.format(color_dict[color], df[color].sum()))
        print('Total {} Cards:     \t\t{}'.format(color_dict[color], len(df[df[color] > 0])))
        print("."*50)
        print('{} Basic Lands:         \t\t{}'.format(mana_dict[color], len(df[df.Type.str.contains(mana_dict[color])])))
        print('{} Total Mana Produced: \t\t{}\n\n'.format(mana_dict[color], df['Pool_'+color].sum()))


    if verbose:
        for type in deck.deck_df.Type.drop_duplicates():
            if 'Land' not in type:
                study_type(df, type, colors=deck.mana_types)


def study_type(df, type, colors=['W','U','B','R','G']):
    type_df = df[df.Type == type]
    print('\n')
    print("*"*50)
    print('\n{} Mana Cost Distribution:'.format(type))
    print('\nNumber of {}: \t{}\n'.format(type, len(type_df)))
    
    if type == 'Creature':
        columns=['ManaCost']+(colors)+['Power','Toughness']
    else:
        columns=['ManaCost']+(colors)

    print(type_df[columns].agg(['mean','median','max','min','sum']))
    print('\nMost expensive {}: \t{} ({})'.format(type, type_df.Name[type_df.ManaCost.idxmax()], type_df.ManaCost.max()))
    print('Least expensive {}: \t{} ({})'.format(type, type_df.Name[type_df.ManaCost.idxmin()], type_df.ManaCost.min()))
    
    if type == 'Creature':
        print('\nMost powerful creature: \t{} ({})'.format(type_df.Name[type_df.Power.idxmax()], type_df.Power.max()))

def break_text(card_df, num_effects=1):
    card_text = card_df.Text.str.split(expand=False)
    type = card.Type
    
    if type in ['Instant', 'Sorcery']:
        stop_words = ['return','destroy','exile','counter','draw','turn','look','discard','search','copy', 'control', 'put']
    
    elif type in ['Artifact', 'Enchantment', 'Planeswalker']:
        stop_words = ['hexproof','haste','look','draw','add','shroud','gets','deathtouch','search','gain','return','token','copy','flying','blocked','exile','tap','cast']
    
    elif type == 'Creature':
        stop_words = ['flying','ninjutsu','draw','return','blocked','search','destroy','copy','cast','exile','play','look','regenerate','greveyard','unblockable','exile','token',
                    'discards','copy','deathtouch','hexproof','lifelink','counter','indestructible','flash','haste','gain','scry','shadow','untap']


def save_deck(deck, filename):
    with open(filename, 'wb') as output:  # Overwrites any existing file.
        pickle.dump(deck, output, pickle.HIGHEST_PROTOCOL)
