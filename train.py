from ia import save_q_table

def train(num_episodes=1000, epsilon_decay=0.99):
    from jeuiacontreia import run_game

    epsilon = 0.1
    
    print("Début de l'entraînement")
    for episode in range(num_episodes):
        print(f"Début de l'épisode {episode + 1}")
        player_score, enemy_score = run_game(auto_play=True, display=True)
        print(f"Match {episode + 1}/{num_episodes} terminé. Score Joueur: {player_score}, Score Ennemi: {enemy_score}")
        epsilon *= epsilon_decay
    
    print("Entraînement terminé.")
    save_q_table()

if __name__ == "__main__":
    train()
