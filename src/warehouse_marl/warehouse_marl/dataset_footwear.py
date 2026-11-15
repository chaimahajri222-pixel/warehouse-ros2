"""
dataset_footwear.py
-------------------
Lecture du jeu de donnees reel "Order Picking Dataset from a Warehouse of a
Footwear Manufacturing Company" (Mendeley Data, doi:10.17632/pf2w725pw3.1,
licence CC BY 4.0 ; decrit dans Data in Brief 2025, doi:10.1016/j.dib.2025.111837)
et conversion en taches de prelevement pour le banc d'essai.

Fichiers utilises (dossier --data-dir, par defaut ~/warehouse_ws/data/footwear
ou la variable d'environnement WAREHOUSE_FOOTWEAR_DIR) :
  - Storage_Location.csv : separateur ',', colonnes originalLocation,
    position, x, y, z (2 292 emplacements) ;
  - Picking_Wave.csv : separateur ';', UTF-8 avec BOM, colonnes waveNumber,
    reference, Size (US), quantityToPick (units), locations, operator
    (215 192 lignes, 9 707 vagues, un emplacement par ligne).

Ordre temporel : le fichier Picking_Wave.csv est en ordre CHRONOLOGIQUE
INVERSE (numeros de vague strictement decroissants ; dates de creation des
commandes, Customer_Order.csv, du 19/10/2023 au 05/01/2023). Les vagues sont
donc remises en ordre chronologique (numero croissant, aucune inversion de
date) ; a l'interieur d'une vague l'ordre des lignes du fichier est conserve.

Separation : les 70 % premieres vagues (chronologiquement) forment la
partie 'train', les 30 % suivantes la partie 'test', sans melange. Dans
'train', les 85 % premieres vagues ('train_fit') servent a l'apprentissage et
les 15 % suivantes ('train_val') a la validation / selection du modele.

Lignes exclues : celles dont l'emplacement n'existe pas dans
Storage_Location.csv (surtout 'RC-01'), faute de coordonnees.

Projection sur le graphe : chaque emplacement reel (x, y) est projete sur le
rack ``shelf_<r>_<c>`` le plus proche apres une mise a l'echelle affine de la
boite englobante des emplacements sur la grille des racks, axe par axe :
    c = arrondi((x - xmin) / (xmax - xmin) * (colonnes - 1))
    r = arrondi((ymax - y) / (ymax - ymin) * (rangees - 1))
(la rangee 0 du graphe est en haut, comme les plus grands y). Ces fonctions
sont monotones : l'ordre des coordonnees reelles est conserve sur chaque axe.
Valable pour build_demo_warehouse (5 x 3) et les grilles plus grandes.
"""

from __future__ import annotations

import csv
import functools
import os
import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

SOURCE = {
    'titre': 'Order Picking Dataset from a Warehouse of a Footwear Manufacturing Company',
    'depot': 'Mendeley Data, doi:10.17632/pf2w725pw3.1 (version 1, 24/12/2024)',
    'article': 'Data in Brief (2025), doi:10.1016/j.dib.2025.111837',
    'licence': 'CC BY 4.0 (page Mendeley Data du jeu)',
}
STORAGE_FILE = 'Storage_Location.csv'
WAVE_FILE = 'Picking_Wave.csv'
TRAIN_FRAC = 0.70
FIT_FRAC = 0.85              # part de 'train' utilisee pour apprendre (le reste : validation)
SPLITS = ('train', 'test', 'train_fit', 'train_val')
_SHELF_RE = re.compile(r'^shelf_(\d+)_(\d+)$')


def default_data_dir() -> str:
    return os.environ.get('WAREHOUSE_FOOTWEAR_DIR',
                          os.path.expanduser('~/warehouse_ws/data/footwear'))


@dataclass(frozen=True)
class StorageLocation:
    code: str
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class PickLine:
    wave: int
    row: int                 # numero de ligne dans Picking_Wave.csv (0 = 1re ligne de donnees)
    reference: str
    size: str
    quantity: int
    location: str
    operator: str


def read_storage_locations(data_dir: Optional[str] = None) -> Dict[str, StorageLocation]:
    path = os.path.join(data_dir or default_data_dir(), STORAGE_FILE)
    out = {}
    with open(path, newline='', encoding='utf-8-sig') as f:
        for r in csv.DictReader(f):
            code = r['originalLocation'].strip()
            out[code] = StorageLocation(code, float(r['x']), float(r['y']), float(r['z']))
    return out


def read_picking_waves(data_dir: Optional[str] = None) -> List[PickLine]:
    """Toutes les lignes de Picking_Wave.csv, dans l'ordre du fichier."""
    path = os.path.join(data_dir or default_data_dir(), WAVE_FILE)
    out = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        for i, r in enumerate(csv.DictReader(f, delimiter=';')):
            out.append(PickLine(int(r['waveNumber']), i, r['reference'].strip(),
                                r['Size (US)'].strip(),
                                int(r['quantityToPick (units)']),
                                r['locations'].strip(), r['operator'].strip()))
    return out


def grid_shape(graph) -> Tuple[int, int]:
    """(rangees, colonnes) des racks shelf_<r>_<c> du graphe."""
    rows = cols = 0
    for n in graph.G.nodes:
        m = _SHELF_RE.match(n)
        if m:
            rows, cols = max(rows, int(m.group(1)) + 1), max(cols, int(m.group(2)) + 1)
    if not rows:
        raise ValueError('le graphe ne contient aucun rack shelf_<r>_<c>')
    return rows, cols


def project_locations(locations: Dict[str, StorageLocation], rows: int,
                      cols: int) -> Dict[str, str]:
    """Emplacement reel -> rack du graphe (projection affine monotone par axe)."""
    xs = [loc.x for loc in locations.values()]
    ys = [loc.y for loc in locations.values()]
    xmin, xmax, ymin, ymax = min(xs), max(xs), min(ys), max(ys)
    out = {}
    for code, loc in locations.items():
        c = round((loc.x - xmin) / (xmax - xmin) * (cols - 1)) if xmax > xmin else 0
        r = round((ymax - loc.y) / (ymax - ymin) * (rows - 1)) if ymax > ymin else 0
        out[code] = f'shelf_{r}_{c}'
    return out


class FootwearDataset:
    def __init__(self, data_dir: Optional[str] = None, train_frac: float = TRAIN_FRAC,
                 fit_frac: float = FIT_FRAC):
        self.data_dir = data_dir or default_data_dir()
        self.locations = read_storage_locations(self.data_dir)
        raw = read_picking_waves(self.data_dir)
        self.n_raw_lines = len(raw)
        # ordre chronologique : numero de vague croissant, puis ordre du fichier
        chrono = sorted(raw, key=lambda p: (p.wave, p.row))
        self.waves: List[int] = list(dict.fromkeys(p.wave for p in chrono))
        self.excluded: Dict[str, int] = {}
        for p in chrono:
            if p.location not in self.locations:
                self.excluded[p.location] = self.excluded.get(p.location, 0) + 1
        n_train = int(round(train_frac * len(self.waves)))
        n_fit = int(round(fit_frac * n_train))
        wave_split = {}
        for i, w in enumerate(self.waves):
            wave_split[w] = 'train' if i < n_train else 'test'
        self.wave_split = wave_split
        fit_waves = set(self.waves[:n_fit])
        self.lines: Dict[str, List[PickLine]] = {s: [] for s in SPLITS}
        for p in chrono:
            if p.location not in self.locations:
                continue
            split = wave_split[p.wave]
            self.lines[split].append(p)
            if split == 'train':
                self.lines['train_fit' if p.wave in fit_waves else 'train_val'].append(p)
        self._projection: Dict[Tuple[int, int], Dict[str, str]] = {}

    # ------------------------------------------------------------------ #
    def waves_of(self, split: str) -> List[int]:
        return list(dict.fromkeys(p.wave for p in self.lines[split]))

    def projection(self, graph) -> Dict[str, str]:
        shape = grid_shape(graph)
        if shape not in self._projection:
            self._projection[shape] = project_locations(self.locations, *shape)
        return self._projection[shape]

    def window_starts(self, split: str, n_tasks: int) -> List[int]:
        """Indices (dans les lignes de ``split``) ou commence une vague et ou
        ``n_tasks`` lignes consecutives tiennent."""
        lines = self.lines[split]
        return [i for i in range(len(lines) - n_tasks + 1)
                if i == 0 or lines[i].wave != lines[i - 1].wave]

    def window(self, split: str, start: int, n_tasks: int) -> List[PickLine]:
        lines = self.lines[split]
        if start < 0 or start + n_tasks > len(lines):
            raise ValueError(f'fenetre [{start}, {start + n_tasks}) hors de {split} '
                             f'({len(lines)} lignes)')
        return lines[start:start + n_tasks]

    def targets(self, graph, split: str, start: int, n_tasks: int) -> List[str]:
        proj = self.projection(graph)
        return [proj[p.location] for p in self.window(split, start, n_tasks)]

    def evenly_spaced_start(self, split: str, n_tasks: int, k: int, n: int) -> int:
        """k-ieme de n fenetres regulierement reparties sur ``split``."""
        starts = self.window_starts(split, n_tasks)
        return starts[(k * len(starts)) // max(n, 1)]

    def stats(self) -> Dict:
        return {
            'lignes_fichier': self.n_raw_lines,
            'vagues': len(self.waves),
            'emplacements': len(self.locations),
            'emplacements_utilises': len({p.location for s in ('train', 'test')
                                          for p in self.lines[s]}),
            'lignes_exclues': sum(self.excluded.values()),
            'lignes_exclues_par_emplacement': dict(sorted(
                self.excluded.items(), key=lambda kv: -kv[1])[:5]),
            **{f'vagues_{s}': len(self.waves_of(s)) for s in SPLITS},
            **{f'lignes_{s}': len(self.lines[s]) for s in SPLITS},
            'premiere_vague_test': self.waves_of('test')[0] if self.lines['test'] else None,
            'derniere_vague_train': self.waves_of('train')[-1] if self.lines['train'] else None,
        }


@functools.lru_cache(maxsize=4)
def load_dataset(data_dir: Optional[str] = None) -> FootwearDataset:
    return FootwearDataset(data_dir)
