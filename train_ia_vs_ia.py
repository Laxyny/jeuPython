from jeuiacontreia import run_game

num_partie = 50  # Nombre de parties à exécuter pour l'entraînement

for episode in range(num_partie):
    player_score, enemy_score = run_game(auto_play=True, display=True, ia_vs_ia=True)
    print(f"Partie {episode + 1}/{num_partie} terminé. Score Joueur: {player_score}, Score Ennemi: {enemy_score}")

print("Entraînement terminé.")
