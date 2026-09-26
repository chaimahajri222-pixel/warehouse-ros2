import gymnasium as gym
from gymnasium import spaces
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import LaserScan

class CentralizedWarehouseEnv(gym.Env):
    """
    Environnement Gymnasium centralisé Multi-Agent avec attribution de tâches (Waypoints).
    """
    def __init__(self):
        super(CentralizedWarehouseEnv, self).__init__()
        
        # ROS 2 Init
        if not rclpy.ok():
            rclpy.init()
        self.node = rclpy.create_node('centralized_task_env_node')
        
        self.robot_names = ['robot1', 'robot2']
        self.stuck_counts = {name: 0 for name in self.robot_names}
        
        # Liste des étagères / zones de livraison (Waypoints de l'entrepôt)
        self.warehouse_waypoints = np.array([
            [2.0, 1.5],    # Étagère A
            [-2.0, 1.5],   # Étagère B
            [2.0, -1.5],   # Zone Dépôt 1
            [-2.0, -1.5]   # Zone Dépôt 2
        ], dtype=np.float32)

        self.targets = {name: np.array([0.0, 0.0], dtype=np.float32) for name in self.robot_names}
        self.prev_distances = {name: 0.0 for name in self.robot_names}

        # ESPACE D'ACTIONS (v_lin, v_ang pour chaque robot)
        low_actions = np.array([0.0, -1.0, 0.0, -1.0], dtype=np.float32)
        high_actions = np.array([0.5, 1.0, 0.5, 1.0], dtype=np.float32)
        self.action_space = spaces.Box(low=low_actions, high=high_actions, dtype=np.float32)

        # ESPACE D'OBSERVATIONS PAR ROBOT:
        # Pos (2) + Vel (2) + Relative Goal (2) + Goal Dist (1) + Scan (10) = 17 par robot
        num_obs_per_robot = 2 + 2 + 2 + 1 + 10
        total_obs = num_obs_per_robot * len(self.robot_names)
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(total_obs,), dtype=np.float32)

        # Publishers
        self.cmd_publishers = {
            name: self.node.create_publisher(Twist, f'/{name}/cmd_vel', 10)
            for name in self.robot_names
        }

        # Données internes
        self.robot_states = {name: {'pos': [0.0, 0.0], 'vel': [0.0, 0.0], 'scan': np.ones(10) * 10.0} for name in self.robot_names}

        # Subscribers
        for name in self.robot_names:
            self.node.create_subscription(Odometry, f'/{name}/odom', lambda msg, n=name: self._odom_callback(msg, n), 10)
            self.node.create_subscription(LaserScan, f'/{name}/scan', lambda msg, n=name: self._scan_callback(msg, n), 10)

    def _assign_new_target(self, robot_name):
        """ Attribue une nouvelle tâche / cible aléatoire au robot """
        idx = np.random.choice(len(self.warehouse_waypoints))
        self.targets[robot_name] = self.warehouse_waypoints[idx].copy()
        
        pos = np.array(self.robot_states[robot_name]['pos'], dtype=np.float32)
        self.prev_distances[robot_name] = np.linalg.norm(self.targets[robot_name] - pos)

    def _odom_callback(self, msg, robot_name):
        self.robot_states[robot_name]['pos'] = [msg.pose.pose.position.x, msg.pose.pose.position.y]
        self.robot_states[robot_name]['vel'] = [msg.twist.twist.linear.x, msg.twist.twist.angular.z]

    def _scan_callback(self, msg, robot_name):
        ranges = np.array(msg.ranges)
        ranges = np.nan_to_num(ranges, posinf=10.0, neginf=0.0)
        idx = np.linspace(0, len(ranges) - 1, 10, dtype=int)
        self.robot_states[robot_name]['scan'] = ranges[idx]

    def _get_observation(self):
        rclpy.spin_once(self.node, timeout_sec=0.01)
        obs = []
        for name in self.robot_names:
            state = self.robot_states[name]
            pos = np.array(state['pos'], dtype=np.float32)
            target = self.targets[name]
            
            rel_goal = target - pos
            dist_goal = np.linalg.norm(rel_goal)

            obs.extend(state['pos'])
            obs.extend(state['vel'])
            obs.extend(rel_goal)
            obs.append(dist_goal)
            obs.extend(state['scan'])

        return np.array(obs, dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        stop_cmd = Twist()
        for pub in self.cmd_publishers.values():
            pub.publish(stop_cmd)
            
        self.stuck_counts = {name: 0 for name in self.robot_names}
        for name in self.robot_names:
            self.robot_states[name]['scan'] = np.ones(10) * 10.0
            self._assign_new_target(name)

        for _ in range(5):
            rclpy.spin_once(self.node, timeout_sec=0.02)
        
        obs = self._get_observation()
        info = {}
        return obs, info

    def step(self, action):
        cmd1 = Twist()
        cmd1.linear.x, cmd1.angular.z = float(action[0]), float(action[1])
        self.cmd_publishers['robot1'].publish(cmd1)

        cmd2 = Twist()
        cmd2.linear.x, cmd2.angular.z = float(action[2]), float(action[3])
        self.cmd_publishers['robot2'].publish(cmd2)

        rclpy.spin_once(self.node, timeout_sec=0.1)

        obs = self._get_observation()
        reward, terminated = self._compute_reward()
        truncated = False
        info = {}

        return obs, reward, terminated, truncated, info

    def _compute_reward(self):
        reward = 0.0
        terminated = False

        for name in self.robot_names:
            scan = self.robot_states[name]['scan']
            vel = self.robot_states[name]['vel']
            pos = np.array(self.robot_states[name]['pos'], dtype=np.float32)
            
            # --- 1. SÉCURITÉ & OBSTACLES ---
            valid_scan = scan[(scan > 0.05) & (scan < 3.5)]
            if len(valid_scan) > 0:
                min_dist = np.min(valid_scan)
                if min_dist < 0.20:
                    reward -= 100.0
                    terminated = True
                    break
                elif min_dist < 0.50:
                    reward -= (0.50 - min_dist) * 3.0

            # --- 2. PROGRESSION VERS LA CIBLE ---
            curr_dist = np.linalg.norm(self.targets[name] - pos)
            progress = self.prev_distances[name] - curr_dist
            reward += progress * 15.0  # Récompense si le robot se rapproche
            self.prev_distances[name] = curr_dist

            # --- 3. ATTEINTE DE LA TÂCHE (OBJECTIF ATTEINT) ---
            if curr_dist < 0.35:
                reward += 200.0
                print(f"🎯 [{name}] Tâche accomplie ! Attribution d'une nouvelle tâche.")
                self._assign_new_target(name)

            # --- 4. GESTION DU BLOCAGE ---
            v_lin = abs(vel[0])
            v_ang = abs(vel[1])

            if v_lin < 0.02 and v_ang < 0.05:
                reward -= 1.0
                self.stuck_counts[name] += 1
            else:
                self.stuck_counts[name] = max(0, self.stuck_counts[name] - 1)

            if self.stuck_counts[name] > 10:
                reward -= 10.0
                cmd_msg = Twist()
                cmd_msg.linear.x = -0.15
                cmd_msg.angular.z = 0.5
                self.cmd_publishers[name].publish(cmd_msg)
                self.stuck_counts[name] = 0

        return reward, terminated

    def close(self):
        self.node.destroy_node()
        rclpy.shutdown()
