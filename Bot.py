import streamlit as st
import random

# --- CLASS POKER BOT ---
class PokerBot:
    def __init__(self, stack, position, bounty):
        self.stack = stack
        self.position = position
        self.bounty = bounty
        self.opponent_profiles = {}

    def evaluate_hand(self, hand):
        """ Évalue la force de la main préflop """
        strong_hands = [('A', 'A'), ('K', 'K'), ('Q', 'Q'), ('J', 'J'), ('A', 'K')]
        medium_hands = [('10', '10'), ('9', '9'), ('A', 'Q'), ('A', 'J'), ('K', 'Q')]
        suited_connectors = [('J', '10'), ('10', '9'), ('9', '8'), ('8', '7')]

        if hand in strong_hands:
            return "premium"
        elif hand in medium_hands:
            return "forte"
        elif hand in suited_connectors:
            return "spéculative"
        elif hand[0] == hand[1]:  # Paires moyennes
            return "moyenne"
        else:
            return "faible"

    def estimate_win_probability(self, hand, community_cards):
        """ Simulation basique pour estimer les chances de victoire """
        strong_cards = ['A', 'K', 'Q', 'J', '10']
        score = sum(1 for card in hand if card in strong_cards)
        if community_cards:
            score += sum(1 for card in community_cards if card in strong_cards)
        return min(0.95, max(0.1, score / 10))

    def make_decision(self, hand, community_cards, actions, pot, opponents):
        """ Prend une décision en combinant plusieurs analyses """
        strength = self.evaluate_hand(hand)
        win_prob = self.estimate_win_probability(hand, community_cards)

        if strength == "premium":
            return "Raise" if "raise" not in actions else "Re-Raise"
        elif strength == "forte":
            return "Call" if "raise" in actions else "Raise"
        elif strength == "spéculative":
            return "Call" if pot < self.stack * 0.3 else "Fold"
        elif strength == "moyenne":
            return "Call" if win_prob > 0.5 else "Fold"
        else:
            return "Fold"

# --- STREAMLIT INTERFACE ---
st.title("🤖 Poker Bot 6-Max KO")

# Saisie des informations de la main
stack = st.slider("💰 Stack du bot", min_value=50, max_value=500, value=100, step=10)
position = st.selectbox("🃏 Position du bot", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
bounty = st.number_input("🏆 Prime Knockout (KO) du bot", min_value=0, value=5)

# Choix des cartes du bot
card1 = st.selectbox("🂠 Première carte", ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2'])
card2 = st.selectbox("🂡 Deuxième carte", ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2'])
hand = (card1, card2)

# Saisie des cartes du flop
community_cards = st.text_input("🃏 Cartes du Flop (ex: A,K,10)", "")

# Actions des adversaires
actions = st.multiselect("🎭 Actions des adversaires", ["raise", "call", "check", "fold"])
pot = st.slider("💵 Taille du pot", min_value=10, max_value=500, value=50, step=10)

# Création du bot et prise de décision
bot = PokerBot(stack=stack, position=position, bounty=bounty)
decision = bot.make_decision(hand, community_cards.split(","), actions, pot, [])

# Affichage de la décision du bot
st.subheader(f"🤖 Décision du bot : **{decision}**")
