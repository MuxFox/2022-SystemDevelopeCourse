"""
Author: Mux
"""

import collections
import enum
import os
import platform
import sys

import PySide6
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

import WindowsGUI

# Configs
if platform.system() == "Windows":
    dirname = os.path.dirname(PySide6.__file__)
    plugin_path = os.path.join(dirname, 'plugins', 'platforms')
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

# Pragma region Constants
PIECE_BUTTON_DEFAULT_STYLE_SHEET = "background-color: light gray;"
PIECE_BUTTON_BLACK_STYLE_SHEET = "background-color: black; color: white"  # set font color to white
PIECE_BUTTON_WHITE_STYLE_SHEET = "background-color: white; color: black"
PIECE_BUTTON_VALID_PLACE_STYLE_SHEET = "background-color: #66CCFF; color: valid"
DEBUG = True


# Pragma region Constants

class Color(enum.Enum):
    Black = 0
    White = 1
    NotSet = 2

    def __str__(self):
        return f"{self.name}"

    __repr__ = __str__


class OthelloGame(QMainWindow):
    def __init__(self):
        super(OthelloGame, self).__init__()
        self.ui = WindowsGUI.Ui_MainWindow()
        self.ui.setupUi(self)
        self.piece_buttons = [
            getattr(self.ui, attrname) for attrname in [
                f"{alpha}{num}" for alpha in "abcdefgh" for num in range(1, 9)
            ]
        ]
        # set piece_buttons's click function
        self.ui.reset_button.clicked.connect(self._reset_game)
        self._current_player = Color.Black
        self._game_check_board = [[Color.NotSet for _ in range(8)] for _ in range(8)]
        # set click function to all piece_button
        for pb in self.piece_buttons:
            pb.clicked.connect((lambda _=None, pb=pb: self._click(pb.objectName())))
        self.pressed_button_cnt = 0
        self._reset_game()

    def _foreach_piece_button(self, func, **kwargs):
        for pb in kwargs["btn_list"] if len(kwargs) != 0 else self.piece_buttons:
            func(pb)

    def _reset_game(self):
        self.ui.GameInfoLabel.setText("Reset/Init game!")

        def _reset_ui(pb: QPushButton):
            pb.setText("")
            pb.setEnabled(True)
            pb.setStyleSheet(PIECE_BUTTON_DEFAULT_STYLE_SHEET)

        self._foreach_piece_button(_reset_ui)
        self._set_piece("d4", Color.White)
        self._set_piece("e5", Color.White)
        self._set_piece("e4", Color.Black)
        self._set_piece("d5", Color.Black)
        self.pressed_button_cnt = 4
        self.ui.TotalCounter.setText(f"Total: {self.pressed_button_cnt}")
        self.ui.BlackPieceCounter.setText(f"Black: {2}")
        self.ui.WhitePieceCounter.setText(f"White: {2}")
        # self._rander_valid_place(Color.Black)

    def _pb_enable(self, b):
        def _able(pb: QPushButton):
            pb.setEnabled(b)

        self._foreach_piece_button(_able)

    def _click(self, pos: str):

        # TODO: Check if piece is placed at a valid position
        # pre_valid_place = self._get_valid_place(self._current_player)
        # if pos not in pre_valid_place:
        #     return

        # Set piece
        self._set_piece(pos, self._current_player)
        # check if winner occurred
        if 64 - self.pressed_button_cnt == 0:
            self.ui.GameInfoLabel.setText(f"Winner is: {self._check_winner()}!")
            self._pb_enable(False)
            return

        # TODO: Rander valid place here
        # self._rander_valid_place(self._current_player)

        # Change next player message
        if self._current_player == Color.Black:
            self.ui.GameInfoLabel.setText("White Next")
        else:
            self.ui.GameInfoLabel.setText("Black Next")

        # flip player
        self._current_player = Color.White if self._current_player == Color.Black else Color.Black
        self.ui.TotalCounter.setText(f"Total: {self.pressed_button_cnt}")
        self.ui.BlackPieceCounter.setText(f"Black: {self._get_piece_count(Color.Black)}")
        self.ui.WhitePieceCounter.setText(f"White: {self._get_piece_count(Color.White)}")

        if DEBUG:
            self._print_game_board()

    def _set_piece(self, position: str, color: Color):
        '''
        1. To set game_board
        2. To set ui
        :param position:
        :param color:
        :return:
        '''
        # For flip color:
        i, j = self._get_indexes(position)
        if self._game_check_board[i][j] is Color.NotSet:
            self._game_check_board[i][j] = color
        else:
            self._game_check_board[i][j] = Color.Black if color == Color.White else Color.White

        # Set UI after click
        cur_pb = getattr(self.ui, position)
        if color == Color.Black:
            cur_pb.setText("B")
            cur_pb.setStyleSheet(PIECE_BUTTON_BLACK_STYLE_SHEET)
        else:
            cur_pb.setText("W")
            cur_pb.setStyleSheet(PIECE_BUTTON_WHITE_STYLE_SHEET)

        self.pressed_button_cnt += 1
        cur_pb.setEnabled(False)

    @staticmethod
    def _get_indexes(position: str) -> tuple:
        """
        Convert Button's name to 2D array indexes
        a1 -> (0, 0)
        :param position: [a-h][1-8]
        :return: a tuple of index in (i row, j colum)
        """
        if len(position) > 2:
            raise ValueError(f"Argument {position} is invalid.")
        return int(position[1]) - 1, "abcdefgh".index(position[0])  # (row, col)

    def _get_color(self, pos: str) -> Color:
        """
        Get the color of a position
        :param pos: position
        :return: Color
        """
        i, j = self._get_indexes(pos)
        return ret if (ret := self._game_check_board[i][j]) is not None else Color.NotSet

    # Pragma region Debug Functions:
    def _print_game_board(self):
        print("".join(["=" for _ in range(88)]))
        print(f"Total pressed button: {self.pressed_button_cnt}")
        print(f"Total unpressed: {self._get_piece_count(Color.NotSet)}")
        print("\n".join([str(row) for row in self._game_check_board]))
        print("".join(["=" for _ in range(88)]))

    # Pragma region Debug Functions

    def _get_piece_count(self, color: Color) -> int:
        return sum([collections.Counter(row)[color] for row in self._game_check_board])

    def _check_winner(self) -> Color:
        return Color.Black if self._get_piece_count(Color.Black) > self._get_piece_count(Color.White) else Color.White

    def _get_colors(self, target: Color):
        ret = []
        for i, r in enumerate( self._game_check_board):
            for j, c in enumerate(r):
                if c == target:
                    ret.append(f"{'abcdefgh'[i]}{j}")

        return ret

    # TODO: Complete this method
    """
    找到每一个棋子的周围的位置s，对每一个位置进行一次是否可以放入棋子的判断
    可以就放入返回的列表中
    """
    def _get_valid_place(self, color: Color) -> list:
        valid_place = list()
        placed_color = self._get_colors(color)
        for pc in placed_color:
             for around in self._get_arounds(pc):
                 # TODO: check around is valid.
                 pass
        return valid_place

    # TODO: Complete this method
    def _check_color_flip(self, pos):
        pass

    def _get_arounds(self, pos: str) -> list:
        r, c = pos[1], pos[0]
        if pos in ["a1", "a8", "h1", "h8"]:
            return {
                "a1": ["a3", "c1"],
                "a8": ["a6", "c8"],
                "h1": ["f1", "h3"],
                "h8": ["f8", "h6"]
            }[pos]
        around = []
        if r in "ab":
            around.append("")

        if r in "gh":
            pass
        around.append(f"{'abcdefgh'['abcdefgh'.index(r) - 2]}{c}")
        around.append(f"{'abcdefgh'['abcdefgh'.index(r) + 2]}{c}")
        return around

    def _rander_valid_place(self, color: Color):
        def bunt_rander(pb: QPushButton):
            pb.setStyleSheet(PIECE_BUTTON_VALID_PLACE_STYLE_SHEET)
            pb.setText("VALID")

        self._foreach_piece_button(bunt_rander, btn_list=[getattr(self.ui, name)
                                                          for name in self._get_valid_place(color)])


if __name__ == "__main__":
    if sys.version_info[1] < 8:
        print("Python version should greater than 3.8")
        exit(-1)
    app = QApplication(sys.argv)
    OthelloGame().show()
    sys.exit(app.exec())
