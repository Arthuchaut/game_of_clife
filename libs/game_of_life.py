from typing import List, Tuple
from datetime import datetime
from random import randint
from enum import Enum, Flag, auto
import sys
from pathlib import Path
from uuid import uuid4
import os
import time


class _Topology(Enum):
    PLANE: Flag = auto()
    SPHERICAL: Flag = auto()


class _State(Enum):
    ALIVE: chr = ' x '
    DEAD: chr = '   '


class Cell:
    _RAND_WEIGHT: int = 5
    STATE: _State = _State

    def __init__(self, *, state: _State = None, i: int = None, j: int = None):
        self.state: _State = state if state else self.gen_random_state()
        self.i = i
        self.j = j

    def born(self) -> None:
        self.state = self.STATE.ALIVE

    def dies(self) -> None:
        self.state = self.STATE.DEAD

    def is_alive(self) -> bool:
        return self.state is self.STATE.ALIVE

    def gen_random_state(self) -> _State:
        if not randint(0, self._RAND_WEIGHT):
            return self.STATE.ALIVE

        return self.STATE.DEAD

    def fmt(self) -> str:
        return f'Cell(state=Cell.STATE.{self.state.name})'

    def __str__(self) -> str:
        return str(self.state.value)


class GameOfLife:
    _SLEEP_TIME: float = 0.01
    TOPOLOGY: _Topology = _Topology

    def __init__(self, area: List[List[Cell]]):
        self._area: List[List[Cell]] = area
        self._area_topology: _Topology = self.TOPOLOGY.SPHERICAL
        self._historic: Historic = None
        self._ref_frame_rate: float = time.time()
        self._ref_duration: float = time.time()
        self._generation: int = 0
        self._frames: int = 0
        self._cached_frames: int = self._frames

    def start(self) -> None:
        if self._historic:
            self._historic.trace(self._historic.area_to_str(self._area))

        self._clear_area()
        self._draw_area()

        while True:
            try:
                time.sleep(self._SLEEP_TIME)
                self._update_area()
                self._clear_area()
                self._draw_area()
                self._print_infos()
            except KeyboardInterrupt:
                if self._historic:
                    self._historic.trace(
                        self._historic.area_to_str(self._area)
                    )

                sys.exit()

    def _draw_area(self) -> None:
        for row in self._area:
            for cell in row:
                print(cell, end='')
            print()

    def _update_area(self) -> None:
        updated_cells: List[Cell] = []

        for i in range(len(self._area)):
            for j in range(len(self._area[i])):
                new_cell: Cell = self._update_cell(self._area[i][j])
                if new_cell:
                    updated_cells += [new_cell]

        for cell, state in updated_cells:
            cell.state = state
            self._area[cell.i][cell.j] = cell

    def _update_cell(self, cell: Cell) -> Tuple[Cell, _State]:
        neighbors: List[Cell] = self._neighbors(cell)
        ngb_alives: int = len([c for c in neighbors if c.is_alive()])

        if ngb_alives == 3:
            if not cell.is_alive():
                return cell, cell.STATE.ALIVE
        elif ngb_alives < 2 or ngb_alives > 3:
            if cell.is_alive():
                return cell, cell.STATE.DEAD

    def _neighbors(self, cell: Cell) -> List[Cell]:
        if self._area_topology is self.TOPOLOGY.SPHERICAL:
            return self._spherical_neighbors(cell)

        return self._plane_neighbors(cell)

    def _plane_neighbors(self, cell: Cell) -> List[Cell]:
        return [
            self._area[i][j]
            for j in range(cell.j - 1, cell.j + 2)
            for i in range(cell.i - 1, cell.i + 2)
            if (j != cell.j or i != cell.i)
            and j > -1
            and j < len(self._area[cell.i])
            and i > -1
            and i < len(self._area)
        ]

    def _spherical_neighbors(self, cell: Cell) -> List[Cell]:
        ngbs: List[Cell] = []

        for i in range(cell.i - 1, cell.i + 2):
            for j in range(cell.j - 1, cell.j + 2):
                if j != cell.j or i != cell.i:
                    i = (
                        0
                        if i >= len(self._area)
                        else len(self._area) - 1
                        if i == -1
                        else i
                    )
                    j = (
                        0
                        if j >= len(self._area[cell.i])
                        else len(self._area[cell.i]) - 1
                        if j == -1
                        else j
                    )

                    ngbs += [self._area[i][j]]

        return ngbs

    def set_topology(self, topology: _Topology) -> None:
        self._area_topology = topology

    def _clear_area(self) -> None:
        os.system('clear')

    def set_historic(self, folder: Path) -> None:
        self._historic = Historic(folder)

    def _print_infos(self) -> None:
        print('---------- INFO ----------')
        self._print_frame_rate()
        self._print_generations()
        self._print_duration()
        print('--------------------------')

    def _print_frame_rate(self) -> None:
        print(f'FRAME RATE: {self._cached_frames} f/s')
        self._frames += 1

        if time.time() - self._ref_frame_rate >= 1:
            self._cached_frames = self._frames
            self._frames = 0
            self._ref_frame_rate = time.time()

    def _print_generations(self) -> None:
        print(f'GENERATIONS: {self._generation} iters')
        self._generation += 1

    def _print_duration(self) -> None:
        print(f'DURATION: {round(time.time() - self._ref_duration, 2)} s')

    @staticmethod
    def from_str(area: str) -> List[List[Cell]]:
        area = area.replace(' ', '')

        return GameOfLife.from_matrix(
            [
                [
                    Cell(
                        state=Cell.STATE.ALIVE
                        if char == 'x'
                        else Cell.STATE.DEAD
                    )
                    for char in line
                ]
                for line in area.split('\n')[1:-1]
            ]
        )

    @staticmethod
    def from_matrix(area: List[List[Cell]]) -> List[List[Cell]]:
        return [
            [
                Cell(i=i, j=j, state=area[i][j].state)
                for j in range(len(area[i]))
            ]
            for i in range(len(area))
        ]

    @staticmethod
    def from_dim(*, term_rows: int, term_cols: int) -> List[List[Cell]]:
        return [
            [Cell(i=i, j=j) for j in range(term_cols)]
            for i in range(term_rows)
        ]


class Historic:
    def __init__(self, his_dir: Path):
        self._hisdir: Path = his_dir
        self._sessid: str = uuid4()

    def trace(self, info: str) -> None:
        with (self._hisdir / f'{self._sessid}.his').open(
            'a', encoding='utf-8'
        ) as f:
            f.write(f'{datetime.now()}\n{info}\n')

    def area_to_str(self, area: List[List[Cell]]) -> str:
        fmt: str = ''

        for row in area:
            for cell in row:
                fmt += ' x ' if cell.is_alive() else ' . '
            fmt += '\n'

        return fmt
