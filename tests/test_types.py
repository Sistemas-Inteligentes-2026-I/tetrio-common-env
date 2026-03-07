from __future__ import annotations

import unittest

from tetrio_env.types import (
    BOARD_COLS,
    BOARD_ROWS,
    BoardState,
    FrameMeta,
    Observation,
    PieceState,
)


class TypesTests(unittest.TestCase):
    def test_board_state_empty_dimensions(self) -> None:
        board = BoardState.empty()

        self.assertEqual(len(board.cells), BOARD_ROWS)
        self.assertEqual(len(board.cells[0]), BOARD_COLS)

    def test_board_state_rejects_invalid_rows(self) -> None:
        with self.assertRaises(ValueError):
            BoardState(cells=((0,) * BOARD_COLS,))

    def test_piece_state_rejects_unknown_piece(self) -> None:
        with self.assertRaises(ValueError):
            PieceState(piece="X", x=0, y=0)

    def test_observation_accepts_valid_shape(self) -> None:
        observation = Observation(
            board=BoardState.empty(),
            frame=FrameMeta(frame_id=1, timestamp_ms=10),
        )

        self.assertFalse(observation.is_game_over)


if __name__ == "__main__":
    unittest.main()
