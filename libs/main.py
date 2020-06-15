from typing import List
from pathlib import Path
from libs.game_of_life import GameOfLife, Cell, Status


class Main:
    @staticmethod
    def run() -> None:
        area: List[List[Cell]] = [
            [
                Cell(status=Status.DEAD),
                Cell(status=Status.DEAD),
                Cell(status=Status.DEAD),
                Cell(status=Status.DEAD),
            ],
            [
                Cell(status=Status.DEAD),
                Cell(status=Status.ALIVE),
                Cell(status=Status.ALIVE),
                Cell(status=Status.ALIVE),
            ],
            [
                Cell(status=Status.ALIVE),
                Cell(status=Status.ALIVE),
                Cell(status=Status.ALIVE),
                Cell(status=Status.DEAD),
            ],
            [
                Cell(status=Status.DEAD),
                Cell(status=Status.DEAD),
                Cell(status=Status.DEAD),
                Cell(status=Status.DEAD),
            ],
        ]

        gol: GameOfLife = GameOfLife(term_rows=60, term_cols=60)
        # gol: GameOfLife = GameOfLife(area=area)
        gol.trace_historic(Path('historic'))
        gol.start()
