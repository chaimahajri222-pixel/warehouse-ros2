import time
import numpy as np
import rclpy
from stable_baselines3 import PPO
from centralized_warehouse_env import CentralizedWarehouseEnv

def evaluate_policy(num_episodes=10):
    print(f"--- DÉBUT DU BENCHMARK SUR {num_episodes} ÉPISODES ---")
    env = CentralizedWarehouseEnv()
    model = PPO.load("ppo_centralized_warehouse.zip", env=env)

    completion_times = []
    success_count = 0

    for episode in range(num_episodes):
        obs, _ = env.reset()
        start_time = time.time()
        done = False
        step_count = 0

        while not done and step_count < 1000:
            action, _ = model.predict(obs, deterministic=True)
            # Appliquer le même facteur d'échelle qu'en déploiement réel
            action[0] *= 2.5
            action[2] *= 2.5
            
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
            step_count += 1
            time.sleep(0.01)

        elapsed_time = time.time() - start_time
        
        if terminated: # Objectif atteint sans dépasser la limite de temps
            success_count += 1
            completion_times.append(elapsed_time)
            print(f"Épisode {episode + 1}: Succès en {elapsed_time:.2f} secondes ({step_count} pas)")
        else:
            print(f"Épisode {episode + 1}: Échec / Timeout ({step_count} pas)")

    env.close()

    # Calcul des statistiques
    success_rate = (success_count / num_episodes) * 100
    mean_time = np.mean(completion_times) if completion_times else 0.0
    std_time = np.std(completion_times) if completion_times else 0.0

    print("\n================ RÉSULTATS DU BENCHMARK ================")
    print(f"Taux de réussite aux waypoints : {success_rate:.1f} %")
    print(f"Temps de parcours moyen        : {mean_time:.2f} s (± {std_time:.2f} s)")
    print("========================================================")

if __name__ == '__main__':
    evaluate_policy(num_episodes=10)

