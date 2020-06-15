from typing import List
from pathlib import Path
from libs.game_of_life import GameOfLife
from libs.area import area


class Main:
    @staticmethod
    def run() -> None:
        gol: GameOfLife = GameOfLife(GameOfLife.from_str(area))
        # gol: GameOfLife = GameOfLife(
        #     GameOfLife.from_dim(term_rows=60, term_cols=60)
        # )
        gol.set_topology(gol.TOPOLOGY.PLANE)
        gol.set_historic(Path('historic'))
        gol.start()

        '''
        SOME NOTES RELATED TO RULES CONFIGURATION

        > LABYRINTH

        if ngb_alives == 2:
            if not cell.is_alive():
                return cell, cell.STATE.ALIVE
        elif ngb_alives > 3:
            if cell.is_alive():
                return cell, cell.STATE.DEAD

        > STABLE VERTICAL LINES

        if ngb_alives == 3:
            if not cell.is_alive():
                return cell, cell.STATE.ALIVE
        elif ngb_alives > 3:
            if cell.is_alive():
                return cell, cell.STATE.DEAD

        > LONG CORRIDORS LABYRINTH

        if ngb_alives == 4:
            if not cell.is_alive():
                return cell, cell.STATE.ALIVE
        elif ngb_alives > 4:
            if cell.is_alive():
                return cell, cell.STATE.DEAD

        > PARTIAL LABYRINTH

        if ngb_alives == 4:
            if not cell.is_alive():
                return cell, cell.STATE.ALIVE
        elif ngb_alives > 5:
            if cell.is_alive():
                return cell, cell.STATE.DEAD
        '''
