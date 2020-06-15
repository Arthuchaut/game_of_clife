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

    def __init__(
        self,
        *,
        term_rows: int = None,
        term_cols: int = None,
        area: List[List[Cell]] = None,
    ):
        self._term_rows: int = term_rows
        self._term_cols: int = term_cols
        self._area: List[List[Cell]] = self._init_area(area)
        self._historic: Historic = None

    def _init_area(self, area: List[List[Cell]]) -> List[List[Cell]]:
        if area is None:
            return [
                [Cell(i=i, j=j) for j in range(self.term_cols)]
                for i in range(self.term_rows)
            ]

        return [
            [
                Cell(i=i, j=j, status=area[i][j].status)
                for j in range(len(area[i]))
            ]
            for i in range(len(area))
        ]

    def start(self) -> None:
        if self._historic:
            self._historic.trace(self._historic.area_to_str(self._area))

        self._clear_area()
        self._draw_area()
        frames: int = 0
        frames_freeze: int = frames
        t1: float = time.time()

        while True:
            time.sleep(self._SLEEP_TIME)
            self._update_area()
            self._clear_area()
            self._draw_area()
            print('FRAMES:', frames_freeze, '/s')

            frames += 1

            if time.time() - t1 >= 1:
                frames_freeze = frames
                frames = 0
                t1 = time.time()

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

    def _clear_area(self) -> None:
        os.system('clear')

    def trace_historic(self, folder: Path) -> None:
        self._historic = Historic(folder)

    @property
    def term_rows(self) -> int:
        if self._term_rows is None:
            return os.get_terminal_size().lines

        return self._term_rows

    @property
    def term_cols(self) -> int:
        if self._term_cols is None:
            return os.get_terminal_size().columns

        return self._term_cols


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
