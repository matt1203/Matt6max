import streamlit as st
import random
import pandas as pd

# --- CLASS POKER BOT ---
class PokerBot:
    def __init__(self, stack_bb, position, bounty, avg_stack, players_left, total_players, buy_in, paid_places):
        self.stack_bb = stack_bb
        self.position = position
        self.bounty = bounty
        self.avg_stack = avg_stack
        self.players_left = players_left
        self.total_players = total_players
        self.buy_in = buy_in
        self.paid_places = paid_places
        self.opponents = []
        self.tournament_stage = self.get_tournament_stage()

    def get_tournament_stage(self):
        """ Détermine le stade du tournoi """
        if self.players_left > self.total_players * 0.5:
            return "Early Game"
        elif self.players_left > self.paid_places + 20:
            return "Mid Game"
        elif self.players_left > self.paid_places:
            return "Approche de la bulle"
        elif self.players_left > 9:
            return "In The Money"
        else:
            return "Table Finale"

    def set_opponents(self, opponents):
        self.opponents = opponents

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

    def decision(self, hand):
        """ Prend une décision selon le stade du tournoi et la situation """
        hand_strength = self.evaluate_hand(hand)
        risk_factor = self.stack_bb / self.avg_stack
        high_bounty_targets = [op for op in self.opponents if op["bounty"] > self.bounty]

        if self.tournament_stage == "Early Game":
            return "Raise" if hand_strength == "premium" else "Call" if hand_strength == "forte" else "Fold"
        elif self.tournament_stage == "Mid Game":
            return "Raise" if hand_strength in ["premium", "forte"] else "Call" if hand_strength == "moyenne" else "Fold"
        elif self.tournament_stage == "Approche de la bulle":
            return "All-in" if risk_factor > 1 and hand_strength == "moyenne" else "Fold"
        elif self.tournament_stage == "In The Money":
            return "All-in" if hand_strength == "premium" else "Raise" if hand_strength == "forte" else "Fold"
        elif self.tournament_stage == "Table Finale":
            return "All-in" if self.stack_bb < 10 and hand_strength in ["premium", "forte"] else "Raise" if hand_strength == "premium" else "Fold"
        return "Fold"

# --- INTERFACE STREAMLIT ---
st.title("♠️ Poker Bot Tournoi MTT KO 🏆")

# Sélection des paramètres du tournoi
buy_in = st.number_input("💵 Prix d'entrée du tournoi ($)", min_value=1, value=10)
total_players = st.slider("👥 Nombre total de joueurs", min_value=50, max_value=10000, value=1000, step=50)
paid_places = st.slider("💰 Nombre de places payées", min_value=10, max_value=500, value=150, step=10)

# Sélection des paramètres du joueur
stack_bb = st.slider("💰 Ton stack (BB)", min_value=1, max_value=200, value=50, step=1)
position = st.selectbox("🎭 Ta position", ["UTG", "MP", "CO", "BTN", "SB", "BB"])
bounty = st.number_input("🏆 Ta prime Knockout (KO)", min_value=0, value=5)
avg_stack = st.slider("📊 Stack moyen du tournoi (BB)", min_value=5, max_value=200, value=40, step=1)
players_left = st.slider("👥 Joueurs restants", min_value=10, max_value=total_players, value=300, step=10)

# Entrée des adversaires
st.subheader("👥 Adversaires")
opponents = []
for i in range(5):
    stack = st.slider(f"💰 Stack Joueur {i+1} (BB)", min_value=1, max_value=200, value=random.randint(10, 100), step=1)
    bounty = st.number_input(f"🏆 Bounty Joueur {i+1}", min_value=0, value=random.randint(1, 10))
    opponents.append({"stack": stack, "bounty": bounty})

# Choix des cartes
st.subheader("🃏 Tes cartes")
card1 = st.selectbox("Première carte", ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2'])
card2 = st.selectbox("Deuxième carte", ['A', 'K', 'Q', 'J', '10', '9', '8', '7', '6', '5', '4', '3', '2'])
hand = (card1, card2)

# Création du bot et prise de décision
bot = PokerBot(stack_bb, position, bounty, avg_stack, players_left, total_players, buy_in, paid_places)
bot.set_opponents(opponents)
decision = bot.decision(hand)

# --- AFFICHAGE GRAPHIQUE TABLE ---
st.subheader("🃏 Table de Poker")
table_html = """
<div style='display: flex; justify-content: center;'>
    <svg width="500" height="500">
        <circle cx="250" cy="250" r="200" fill="green" />
        <text x="250" y="30" text-anchor="middle" fill="white">Joueur 1</text>
        <text x="50" y="250" text-anchor="middle" fill="white">Joueur 2</text>
        <text x="450" y="250" text-anchor="middle" fill="white">Joueur 3</text>
        <text x="250" y="470" text-anchor="middle" fill="white">Joueur 4</text>
        <text x="100" y="400" text-anchor="middle" fill="white">Joueur 5</text>
        <text x="400" y="400" text-anchor="middle" fill="white">Toi</text>
    </svg>
</div>
"""
st.markdown(table_html, unsafe_allow_html=True)

st.subheader(f"🤖 Décision du bot : **{decision}**")
