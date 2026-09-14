"""
train_drl.py
------------
Script d'ENTRAINEMENT HORS-LIGNE de l'agent DQN sur l'environnement
WarehouseTaskAllocationEnv. Ce n'est PAS un noeud ROS2 : on entraine en
pur Python (rapide, reproductible, sans lancer Gazebo), puis on exporte
le modele (.pt) qui sera charge par drl_allocator_node.py en inference
temps-reel dans la simulation ROS2.

Usage :
    ros2 run warehouse_marl train_drl --episodes 500 --out model.pt
ou directement :
    python3 warehouse_marl/drl/train_drl.py --episodes 500 --out model.pt

Produit egalement un log CSV (episode, reward_total, avg_path_cost) que tu
peux directement exploiter pour les courbes de convergence de ton memoire.
"""

import argparse
import csv
import os

import numpy as np

from warehouse_marl.drl.env import WarehouseTaskAllocationEnv
from warehouse_marl.drl.dqn_agent import DQNAgent


def parse_args():
    p = argparse.ArgumentParser(description="Entrainement DQN - allocation de taches entrepot")
    p.add_argument('--episodes', type=int, default=500)
    p.add_argument('--n-agents', type=int, default=3)
    p.add_argument('--tasks-per-episode', type=int, default=40)
    p.add_argument('--batch-size', type=int, default=64)
    p.add_argument('--target-update-every', type=int, default=10)
    p.add_argument('--out', type=str, default='warehouse_dqn.pt')
    p.add_argument('--log-csv', type=str, default='training_log.csv')
    p.add_argument('--seed', type=int, default=0)
    return p.parse_args()


def main(args=None):
    args = parse_args()

    env = WarehouseTaskAllocationEnv(
        n_agents=args.n_agents,
        n_tasks_per_episode=args.tasks_per_episode,
        seed=args.seed,
    )
    obs_dim = env.observation_space.shape[0]
    n_actions = env.action_space.n

    agent = DQNAgent(obs_dim=obs_dim, n_actions=n_actions)

    log_rows = []
    for episode in range(1, args.episodes + 1):
        obs, _ = env.reset(seed=args.seed + episode)
        total_reward = 0.0
        path_costs = []
        done = False

        while not done:
            action = agent.select_action(obs)
            next_obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated

            agent.remember(obs, action, reward, next_obs, done)
            agent.train_step(batch_size=args.batch_size)

            obs = next_obs
            total_reward += reward
            path_costs.append(info['path_cost'])

        agent.decay_epsilon()
        if episode % args.target_update_every == 0:
            agent.update_target()

        avg_cost = float(np.mean(path_costs))
        log_rows.append((episode, total_reward, avg_cost, agent.epsilon))

        if episode % 25 == 0 or episode == 1:
            print(f"[ep {episode:4d}] reward={total_reward:8.2f}  "
                  f"avg_path_cost={avg_cost:6.2f}  epsilon={agent.epsilon:.3f}")

    agent.save(args.out)
    print(f"\nModele sauvegarde -> {os.path.abspath(args.out)}")

    with open(args.log_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['episode', 'total_reward', 'avg_path_cost', 'epsilon'])
        writer.writerows(log_rows)
    print(f"Log d'entrainement -> {os.path.abspath(args.log_csv)}")


if __name__ == '__main__':
    main()
