from jeuiacontreia import run_game

num_episodes = 1000  # Nombre de parties à exécuter pour l'entraînement

for episode in range(num_episodes):
    player_score, enemy_score = run_game(auto_play=True, display=True, ia_vs_ia=True)
    print(f"Episode {episode + 1}/{num_episodes} terminé. Score Joueur: {player_score}, Score Ennemi: {enemy_score}")

print("Entraînement terminé.")
