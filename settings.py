class Settings:
    def __init__(self):
        self.WINDOW_TITLE = "Big Shoes"
        self.WINDOW_ICON = "icon.png"

        self.CONNECTED_TO_TEXT = "Connected to "
        self.DISCONNECTED_TEXT = "Disconnected."

        self.STEPGRAPH_DEFAULT_SIZE = (1500, 400)
        self.STEPGRAPH_FONT = None

        self.BACKGROUND_COLOR = (0, 0, 0)
        self.GRAPH_BACKGROUND_COLOR_1 = (0, 0, 0)
        self.GRAPH_BACKGROUND_COLOR_2 = (16, 16, 16)
        self.BORDER_LINE_COLOR = (255, 255, 255)
        self.GRIDLINE_COLOR = (32, 32, 32)
        self.GRIDLINE_PREEMPTIVE_COLOR = (128, 0, 128)
        self.GRAPH_LABEL_COLOR = (255, 255, 255)
        self.BATTLE_CHECK_COLOR = (0, 128, 128)
        self.BATTLE_CHECK_PREEMPTIVE_COLOR = (196, 0, 196)
        self.BATTLE_CHECK_SELECTED_OUTLINE_COLOR = (196, 196, 0)
        self.WALK_EXTRAPOLATION_COLOR = (64, 255, 64)
        self.RUN_EXTRAPOLATION_COLOR = (64, 64, 255)
        self.BATTLE_MARK_COLOR = (255, 64, 64)
        self.POSITION_MARK_COLOR = (255, 0, 0)

        self.LEFT_OFFSET = 36
        self.BOTTOM_OFFSET = 18
        self.STEP_PER_GRIDLINE = 2
        self.X_GRIDLINE_WIDTH = 12
        self.X_GRIDLINES_PER_TEXT = 2
        self.MIN_TOP_DANGER = 100
        self.MAX_TOP_DANGER = 65536
        self.DEFAULT_TOP_DANGER = 6000
        self.Y_GRIDLINE_HEIGHT = 12
        self.SCROLL_STEPS = self.STEP_PER_GRIDLINE
        self.HOLD_SHIFT_SCROLL_MULTIPLIER = 10
        self.UPDATES_PER_SECOND = 30
        self.DEFAULT_TRACK_LEFT_OFFSET = 4

        self.DISPLAY_PREEMPTIVE_BATTLE_CHECKS_DEFAULT = True
        self.DISPLAY_PREEMPTIVE_STEPIDS_DEFAULT = False
        self.DISPLAY_EXTRAPOLATION_DEFAULT = True
        self.DISPLAY_BATTLE_MARKS_DEFAULT = True
