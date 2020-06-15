from typing import List, Tuple
from random import randint
from enum import Enum
from pathlib import Path
from uuid import uuid4
import os
import time


class Status(Enum):
    ALIVE: chr = 'o'
    DEAD: chr = '  '


class Cell:
    _RAND_WEIGHT: int = 5

    def __init__(self, *, status: Status = None, i: int = None, j: int = None):
        self.status: Status = status if status is not None else self.gen_random_status()
        self.i = i
        self.j = j

    def born(self) -> None:
        self.status = Status.ALIVE

    def dies(self) -> None:
        self.status = Status.DEAD

    def is_alive(self) -> bool:
        return self.status is Status.ALIVE

    def gen_random_status(self) -> Status:
        if not randint(0, self._RAND_WEIGHT):
            return Status.ALIVE

        return Status.DEAD

    def fmt(self) -> str:
        return f'Cell(status=Status.{self.status.name})'

    def __str__(self) -> str:
        return str(self.status.value)


class GameOfLife:
    _SLEEP_TIME: float = 0.01

    def __init__(self, area: List[List[Cell]]):
        self._area: List[List[Cell]] = area
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
            time.sleep(self._SLEEP_TIME)
            self._update_area()
            self._clear_area()
            self._draw_area()
            self._print_infos()

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

        for cell, status in updated_cells:
            cell.status = status
            self._area[cell.i][cell.j] = cell

    def _update_cell(self, cell: Cell) -> Tuple[Cell, Status]:
        neighbors: List[Cell] = self._neighbors(cell)
        ngb_alives: int = len([c for c in neighbors if c.is_alive()])

        if ngb_alives == 3:
            if not cell.is_alive():
                return cell, Status.ALIVE
        elif ngb_alives < 2 or ngb_alives > 3:
            if cell.is_alive():
                return cell, Status.DEAD

    def _neighbors(self, cell: Cell) -> List[Cell]:
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

    def _clear_area(self) -> None:
        os.system('clear')

    def trace_historic(self, folder: Path) -> None:
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
        return GameOfLife.from_matrix(
            [
                [
                    Cell(status=Status.ALIVE if char == 'x' else Status.DEAD)
                    for char in line
                ]
                for line in area.split('\n')[1:-1]
            ]
        )

    @staticmethod
    def from_matrix(area: List[List[Cell]]) -> List[List[Cell]]:
        return [
            [
                Cell(i=i, j=j, status=area[i][j].status)
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
        (self._hisdir / f'{self._sessid}.his').write_text(
            info, encoding='utf-8'
        )

    def area_to_str(self, area: List[List[Cell]]) -> str:
        fmt: str = '[\n'

        for row in area:
            fmt += '\t[\n'
            for cell in row:
                fmt += f'\t\t{cell.fmt()},\n'
            fmt += '\t],\n'

        fmt += ']'

        return fmt
