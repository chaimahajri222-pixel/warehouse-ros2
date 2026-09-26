import os
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize
from stable_baselines3.common.callbacks import CheckpointCallback
from centralized_warehouse_env import CentralizedWarehouseEnv

def main():
    print("Initialisation de l'environnement Gym Centralisé...")
    raw_env = CentralizedWarehouseEnv()
    env = DummyVecEnv([lambda: raw_env])
    
    # Application de la normalisation
    env = VecNormalize(env, norm_obs=True, norm_reward=True, clip_obs=10.0)

    print("Création du modèle PPO...")
    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=0.0003,
        n_steps=2048,
        batch_size=64,
        tensorboard_log="./ppo_warehouse_tensorboard/",
        device="auto"
    )

    print("Début de l'entraînement...")
    try:
        # L'entraînement sauvegarde régulièrement
        model.learn(total_timesteps=50000)
    except KeyboardInterrupt:
        print("\nEntraînement interrompu manuellement par l'utilisateur.")
    finally:
        print("Sauvegarde du modèle et des paramètres de normalisation...")
        model.save("ppo_centralized_warehouse")
        env.save("vec_normalize.pkl")
        print("Sauvegarde réussie !")

if __name__ == '__main__':
    main()
