import time
import rclpy
from stable_baselines3 import PPO
from centralized_warehouse_env import CentralizedWarehouseEnv

def main():
    print("Initialisation de l'environnement Gym avec Waypoints...")
    env = CentralizedWarehouseEnv()

    print("Chargement du modèle entraîné avec attribution de tâches...")
    model = PPO.load("ppo_centralized_warehouse.zip", env=env)

    print("\n🚀 Déploiement de la politique optimisée !")
    print("Appuyez sur Ctrl+C pour arrêter le test.\n")

    obs, _ = env.reset()
    
    try:
        while rclpy.ok():
            # Prédiction déterministe des actions
            action, _states = model.predict(obs, deterministic=True)

            # Amplification des vitesses
            action[0] *= 2.5  # Vitesse lin Robot 1
            action[2] *= 2.5  # Vitesse lin Robot 2

            # Affichage des vitesses
            print(f"Vitesse R1: [lin: {action[0]:.2f}, ang: {action[1]:.2f}] | Vitesse R2: [lin: {action[2]:.2f}, ang: {action[3]:.2f}]", end='\r')

            # Application de l'action
            obs, reward, terminated, truncated, info = env.step(action)

            if terminated or truncated:
                print("\nRéinitialisation de l'épisode...")
                obs, _ = env.reset()

            time.sleep(0.01)
       

    except KeyboardInterrupt:
        print("\nArrêt du test par l'utilisateur.")
    finally:
        env.close()

if __name__ == '__main__':
    main()

