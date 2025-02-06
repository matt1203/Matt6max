import streamlit as st
import eval7
import random

# Profils des joueurs
PLAYER_PROFILES = {
    "NIT": {"VPIP": 10, "PFR": 8},
    "TAG": {"VPIP": 18, "PFR": 15},
    "LAG": {"VPIP": 28, "PFR": 22},
    "FISH": {"VPIP": 40, "PFR": 5},
    "MANIAC": {"VPIP": 50, "PFR": 40}
}

# Monte Carlo pour calculer l'équité
def monte_carlo_equity(hand, board, num_simulations=10000):
    deck = eval7.Deck()
    known_cards = hand + board
    for card in known_cards:
        deck.cards.remove(card)

    wins, ties, total = 0, 0, 0
    for _ in range(num_simulations):
        deck.shuffle()
        opp_hand = [deck.pop(), deck.pop()]
        remaining_board = board.copy()

        while len(remaining_board) < 5:
            remaining_board.append(deck.pop())

        our_score = eval7.evaluate(hand + remaining_board)
        opp_score = eval7.evaluate(opp_hand + remaining_board)

        if our_score > opp_score:
            wins += 1
        elif our_score == opp_score:
            ties += 1
        total += 1

        deck.cards.extend(opp_hand + remaining_board[len(board):])

    return (wins + ties / 2) / total * 100

# Fonction de prise de décision
def suggest_action(equity, pot_odds, bounty_factor, stack_size, opp_stack, profile):
    if bounty_factor > 0 and stack_size >= opp_stack:
        return "PUSH pour le BOUNTY" if equity > 35 else "FOLD"
    
    if profile == "MANIAC":
        return "CALL LIGHT / PUSH" if equity > 30 else "FOLD"
    if profile == "NIT" and equity > 60:
        return "RAISE / CALL"
    if profile in ["TAG", "LAG"]:
        return "RAISE AGRESSIF" if equity > 40 else "FOLD"
    
    if equity > pot_odds + 10:
        return "RAISE / SHOVE" if stack_size < 20 else "RAISE"
    elif equity > pot_odds:
        return "CALL"
    else:
        return "FOLD"

# Interface Web avec Streamlit
st.title("🃏 PokerBot MTT 6-Max KO - Web App")

hand_str = st.text_input("Votre main (ex: Ah Ks)")
board_str = st.text_input("Board (Flop/Turn/River)")
stack_size = st.number_input("Votre stack (BB)", min_value=0.0, value=50.0)
opp_stack = st.number_input("Stack adverse (BB)", min_value=0.0, value=50.0)
bounty = st.number_input("Bounty adverse (€)", min_value=0.0, value=10.0)
pot_size = st.number_input("Taille du pot", min_value=0.0, value=10.0)
bet_size = st.number_input("Mise adverse", min_value=0.0, value=5.0)
profile = st.selectbox("Profil adverse", ["NIT", "TAG", "LAG", "FISH", "MANIAC"])

if st.button("Analyser la main"):
    try:
        hand = [eval7.Card(card) for card in hand_str.split()]
        board = [eval7.Card(card) for card in board_str.split()] if board_str else []
    except:
        st.error("Format incorrect des cartes !")
        st.stop()

    equity = monte_carlo_equity(hand, board)
    pot_odds = (bet_size / (pot_size + bet_size)) * 100 if bet_size > 0 else 0
    bounty_factor = (bounty / (stack_size + bounty)) * 100 if bounty > 0 else 0
    action = suggest_action(equity, pot_odds, bounty_factor, stack_size, opp_stack, profile)

    st.success(f"✅ **Équité estimée** : {equity:.2f}%")
    st.info(f"💰 **Odds du pot** : {pot_odds:.2f}%")
    st.warning(f"🎯 **Facteur Bounty** : {bounty_factor:.2f}%")
    st.subheader(f"🎲 **Action recommandée** : {action} ✅")
