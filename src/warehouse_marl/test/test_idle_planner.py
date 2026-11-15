"""idle_planner (idle_mode dans ROS) : meme decision que le banc v4
(BenchmarkV4._choose_park) pour un meme etat de flotte et de demande."""
import os
import random

import pytest

from warehouse_marl.allocation_benchmark import Task
from warehouse_marl.drl.v4_dqn import V4DQN
from warehouse_marl.drl.v4_sim import N_IDLE_FEATURES, BenchmarkV4
from warehouse_marl.idle_planner import choose_idle_point
from warehouse_marl.warehouse_graph import build_demo_warehouse

MODEL = os.path.expanduser('~/warehouse_ws/drl_v4/idle/selected_idle.pt')


def _agents():
    import torch
    untrained = V4DQN('idle', N_IDLE_FEATURES, seed=0)
    agents = [('non_entraine', untrained)]
    torch.manual_seed(3)
    noisy = V4DQN('idle', N_IDLE_FEATURES, seed=1)
    with torch.no_grad():
        for prm in noisy.q.parameters():
            prm.add_(0.3 * torch.randn_like(prm))
    agents.append(('aleatoire', noisy))
    if os.path.isfile(MODEL):
        from warehouse_marl.drl.v4_dqn import load_v4_model
        agents.append(('retenu', load_v4_model(MODEL, 'idle')))
    return agents


@pytest.mark.parametrize('name,agent', _agents())
def test_same_choice_as_simulator(name, agent):
    g = build_demo_warehouse(-1.5, -1.0)
    shelves = [n for n, d in g.G.nodes(data=True) if d['node_type'] == 'shelf']
    nodes = list(g.G.nodes)
    rng = random.Random(7)
    for _ in range(60):
        ids = [f'robot{i + 1}' for i in range(rng.choice([1, 2, 3]))]
        st = {i: {'node': rng.choice(nodes), 'park': rng.choice([None] + nodes),
                  'idle': rng.random() < 0.6} for i in ids}
        st['robot1']['idle'] = True
        counts = {s: rng.randint(0, 5) for s in rng.sample(shelves, 4)}
        n_open = rng.randint(0, 3)
        for mode, sim_mode in (('centre', 'centre_de_demande'), ('drl', 'drl_idle')):
            got, _ = choose_idle_point(g, 'robot1', st, mode, agent=agent,
                                       demand_counts=counts, n_open=n_open)
            sim = BenchmarkV4('greedy_pair', g, len(ids), 1.0, 1, seed=0, speed=0.5,
                              idle_mode=sim_mode, idle_agent=agent)
            for rid, r in zip(ids, sim.robots):
                r.node, r.park, r.queue = st[rid]['node'], st[rid]['park'], []
                r.task = None if st[rid]['idle'] else Task('x', r.node, 1.0, 0.0)
            sim.open = [Task(f'o{i}', 'charging_dock', 1.0, 0.0) for i in range(n_open)]
            sim.tasks = [Task(f'k{s}{j}', s, 1.0, 0.0) for s, c in counts.items()
                         for j in range(c)]
            assert got == sim._choose_park(sim.robots[0]), (name, mode, st, counts)


def test_untrained_drl_is_centre_and_stay_is_here():
    g = build_demo_warehouse(-1.5, -1.0)
    st = {'robot1': {'node': 'shelf_0_0', 'park': None, 'idle': True}}
    counts = {'shelf_4_2': 4, 'shelf_4_1': 2}
    centre, _ = choose_idle_point(g, 'robot1', st, 'centre', demand_counts=counts)
    drl0, _ = choose_idle_point(g, 'robot1', st, 'drl', agent=V4DQN('idle', N_IDLE_FEATURES),
                                demand_counts=counts)
    assert drl0 == centre
    assert choose_idle_point(g, 'robot1', st, 'stay')[0] == 'shelf_0_0'
