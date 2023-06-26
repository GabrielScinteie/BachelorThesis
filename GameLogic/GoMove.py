class GoMove:
    def __init__(self, row, column, player):
        self.row = row
        self.column = column
        self.player = player

    def __repr__(self):
        return "Player:{0} Row:{1} Column:{2}".format(
            self.player,
            self.row,
            self.column)
