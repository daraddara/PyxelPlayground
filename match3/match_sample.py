import pyxel
from enum import Enum

DEBUG=False
BGM = True

class Debug :
    delete_count = 0
    extend_val = 0
    def print(str) :
        if DEBUG :
            print(str)

class State(Enum) :
    START = 0
    SELECT = 1
    CHECK1 = 2
    DELETE = 3
    CHECK2 = 4
    DROPDOWN = 5
    REFILL = 6
    WAIT_DROPPED_ALL = 7
    CHECK_TENPAI = 8
    NO_MORE_MOVE = 9
    TITLE = 99
    GAMEOVER = 100
    WAIT_RESTART = 101

class Position :
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.x == other.x and self.y == other.y
        return False

class Chip :
    def __init__(self, x, y, type, dst_x=None, dst_y=None) :
        self.type = type
        self.select = False
        self.match = False
        self.tenpai = False
        self.hint = False   #ヒント表示
        self.update_delta = 3
       # 描画位置
        self.pos_x = x
        self.pos_y = y

       # 移動位置
        self.dst_x = self.pos_x if dst_x is None else dst_x
        self.dst_y = self.pos_y if dst_y is None else dst_y

    def draw_base(self, col=None):
        col = col if col is not None else self.type

        if self.match and pyxel.frame_count % 4 == 0 :
            pyxel.blt(self.pos_x, self.pos_y, 0, 0, 0, App.CHIP_SIZE, App.CHIP_SIZE)
        else :
            pyxel.blt(self.pos_x, self.pos_y, 0, col*App.CHIP_SIZE, 16, App.CHIP_SIZE, App.CHIP_SIZE, 0)

        if self.select :
            pyxel.blt(self.pos_x, self.pos_y, 0, 0, 1*App.CHIP_SIZE, App.CHIP_SIZE, App.CHIP_SIZE, 0)

        if self.hint and self.tenpai :
            pyxel.rectb(self.pos_x, self.pos_y, App.CHIP_SIZE, App.CHIP_SIZE, 11)

        if DEBUG :
            pyxel.text(self.pos_x+2, self.pos_y+2, f"{col}", 10 )


    def draw_delete(self):
        pyxel.rect(self.pos_x, self.pos_y, App.CHIP_SIZE, App.CHIP_SIZE, 7)

    def is_dropped(self):
        return self.pos_y == self.dst_y

    def is_moved(self):
        return self.pos_x == self.dst_x and self.pos_y == self.dst_y

    def set_dst(self, x, y):
        self.dst_x = x
        self.dst_y = y

    def set_update_delta(self, val) :
        self.update_delta = val

    def update_pos(self):
        if self.pos_y < self.dst_y :
            self.pos_y += self.update_delta
            if self.pos_y > self.dst_y :
                self.pos_y = self.dst_y
        elif self.pos_y > self.dst_y :
            self.pos_y -= self.update_delta
            if self.pos_y < self.dst_y :
                self.pos_y = self.dst_y

        if self.pos_x < self.dst_x :
            self.pos_x += self.update_delta
            if self.pos_x > self.dst_x :
                self.pos_x = self.dst_x
        elif self.pos_x > self.dst_x :
            self.pos_x -= self.update_delta
            if self.pos_x < self.dst_x :
                self.pos_x = self.dst_x


    def draw(self) :
        self.update_pos()
        self.draw_base()

class SoundEffect:
    def __init__(self, ch):
        self.ch = ch

        self.init_sound()

    def init_sound(self):
        pyxel.sound(0).set("b-2", "s", "3", "n", 30)
        pyxel.sound(1).set("c3", "s", "3", "n", 30)
        pyxel.sound(2).set("d3", "s", "3", "n", 30)
        pyxel.sound(3).set("e-3", "s", "3", "n", 30)
        pyxel.sound(4).set("f3", "s", "4", "n", 30)
        pyxel.sound(5).set("g3", "s", "4", "n", 30)
        pyxel.sound(6).set("a3", "s", "4", "n", 30)
        pyxel.sound(7).set("b-3", "s", "5", "n", 30)
        self.test_play_start = False
        self.test_sound_no = 0

    def get_score(self, no):
        pyxel.play(self.ch, min(no, 7))

    def bad(self):
        pyxel.play(self.ch, 20)

    def swap(self):
        pyxel.play(self.ch, 21)

    def undo_swap(self):
        pyxel.play(self.ch, 22)

    def gameover(self) :
        pyxel.play(self.ch, 23)

    def test_play(self):
        if self.test_play_start:
            if pyxel.frame_count % 20 == 0:
                pyxel.play(0, self.test_sound_no)
                self.test_sound_no += 1

        if self.test_sound_no > 8:
            self.test_sound_no = 0
            self.test_play_start = False

class Gage:
    def __init__(self, x, y, width, height, frame_col, inside_col) :
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.frame_col = frame_col

        self.inside_col = inside_col
        self.inside_x = x + 1
        self.inside_y = 0
        self.inside_width = width - 2
        self.inside_height = 0

        self.val = 0

    def update(self, val) :
        bar_length = val * (self.height-1)
        self.inside_y = self.y + self.height - bar_length
        self.inside_height = bar_length


    def set_color(self, col) :
        self.inside_col = col

    def draw(self):
        pyxel.rect(self.x, self.y, self.width, self.height, 0)
        pyxel.rect(self.inside_x, self.inside_y, self.inside_width, self.inside_height, self.inside_col)


class App:
    TITLE = "Match3"

    FPS = 60

    CHIP_SIZE = 16

    BOX_WIDTH = 7
    BOX_HEIGHT = 9
    BOX_X = 16
    BOX_Y = 16
    SCREEN_WIDTH = BOX_X * 2 + CHIP_SIZE * BOX_WIDTH
    SCREEN_HEIGHT = BOX_Y + CHIP_SIZE * BOX_HEIGHT

    GAME_TIME = 60

    if DEBUG :
        SCREEN_WIDTH = 240

    def __init__(self):
        self.x=10
        self.bg = 0

        self.top_text = ""
        self.top_text_color = 7

        self.top_extra_text =""
        self.top_extra_text_color = 7

        self.center_texts = []
        self.center_text_color = 5

        self.score=0
        self.combo=0

        self.game_timer_load = App.GAME_TIME * App.FPS
        self.game_timer_val = 0

        self.box = []
        self.max_type = 6
        self.select = 0

        self.drag = None
        self.undo = None
        self.state = State.TITLE
        self.down_counter = 0

        self.timer_action_table = {}

        self.fast_bgm = False

        pyxel.init(App.SCREEN_WIDTH, App.SCREEN_HEIGHT, title=App.TITLE, fps=App.FPS)

        pyxel.load("match_resource.pyxres")

        self.se = SoundEffect(3)

        self.init_box()
        self.gage = Gage(5, App.BOX_Y, 6, App.SCREEN_HEIGHT - App.BOX_Y, 1, 6)

        pyxel.mouse(True)

        pyxel.run(self.update, self.draw)

    def init_game(self) :
        self.score = 0
        self.init_bgm()
        self.gage.set_color(6)
        self.clear_center_text()
        self.init_box()
        self.drag = None
        self.drag2 = None
        self.load_game_timer()

    def init_bgm(self) :
        pyxel.playm(0, loop = True)
        self.fast_bgm = False

    def init_box(self):
        while True :
            self.box = [[Chip(self.x2posx(x), self.y2posy(y-1), pyxel.rndi(1, self.max_type), self.x2posx(x),self.y2posy(y)) for y in range(App.BOX_HEIGHT)] for x in range(App.BOX_WIDTH)]

            while self.check_match() :
                self.delete_chips()
                self.refill_chips()

            if self.check_tenpai_all() > 0:
                break

    def draw_bg(self) :
        for x in range(0, App.SCREEN_WIDTH, 16) :
            for y in range(0, App.SCREEN_HEIGHT, 16) :
                pyxel.blt(x, y, 0, 0, 32, 16, 16)

    def load_game_timer(self) :
        self.game_timer_val = self.game_timer_load


    def change_fast_bgm(self):
        (sound, note) = pyxel.play_pos(0)
        pyxel.stop()
        tick = sound * 32 + note
        pyxel.playm(1, tick=tick, loop=True)
        self.fast_bgm = True

    def update_game_timer(self) :
        if self.game_timer_val > 0 :
            self.game_timer_val -= 1

        if not self.fast_bgm and self.game_timer_val < self.game_timer_load * 0.25 :
            self.change_fast_bgm()
            self.gage.set_color(8)

    def extend_game_timer(self, num) :
        self.game_timer_val += num
        Debug.extend_val += num

    def is_gameover(self) :
        return self.game_timer_val == 0

    def set_counter(self, val):
        self.down_counter = val

    def update_counter(self):
        if self.down_counter > 0 :
            self.down_counter -= 1

    def is_expire(self) :
        return self.down_counter == 0

    def pos2boxidx(self, x, y) :
        """グローバル座標からbox内indexに変換"""
        idx_x = (x - App.BOX_X) // App.CHIP_SIZE
        idx_y = (y - App.BOX_Y) // App.CHIP_SIZE

        return Position(idx_x, idx_y)

    def x2posx(self, x) :
        pos_x = App.BOX_X + App.CHIP_SIZE * x
        return pos_x

    def y2posy(self, y) :
        pos_y = App.BOX_Y + App.CHIP_SIZE * y
        return pos_y


    def GetChipType(self, Position) :
        return self.box[Position.x][Position.y].type

    def SelectChip(self, Position) :
        self.drag = Position
        self.box[Position.x][Position.y].select = True

    def SelectChip2(self, Position) :
        self.drag2 = Position

    def release_chip(self) :
        self.box[self.drag.x][self.drag.y].select = False
        self.drag = None
        self.drag2 = None

    def swap_element(self, a, b):
        tmp = a
        a = b
        b = tmp

    def swap_chip(self, undo=False):

        if undo :
            self.drag = self.undo
            self.undo = None
        else :
            self.undo = self.drag

            self.box[self.drag.x][self.drag.y].select = False

        tmp = self.get_drag_chip()
        self.box[self.drag.x][self.drag.y] = self.get_drag2_chip()
        self.box[self.drag2.x][self.drag2.y] = tmp

        self.box[self.drag.x][self.drag.y].set_dst(self.x2posx(self.drag.x), self.y2posy(self.drag.y))
        self.box[self.drag2.x][self.drag2.y].set_dst(self.x2posx(self.drag2.x), self.y2posy(self.drag2.y))

        self.drag = None

    def undo_swap(self):
        self.swap_chip(undo=True)
        return

    def click_in_box(self):
        if (App.BOX_X <= pyxel.mouse_x < App.BOX_X+App.BOX_WIDTH*App.CHIP_SIZE and
            App.BOX_Y <= pyxel.mouse_y <App.BOX_Y+App.BOX_HEIGHT*App.CHIP_SIZE) :
            return True

        return False


    def get_chip(self, x, y):
        if x in range(App.BOX_WIDTH) and y in range(App.BOX_HEIGHT) :
            return self.box[x][y]
        else :
            return Chip(x, y, 100*x + y )   # 範囲外用のダミー、typeは識別できる値(描画することはない)


    def check_tenpai(self, x, y):
        # 右方向2連
        if self.get_chip(x+1, y).type == self.get_chip(x+2, y).type :
            if (self.get_chip(x+1, y).type == self.get_chip(x, y-1).type or
                self.get_chip(x+1, y).type == self.get_chip(x, y+1).type or
                self.get_chip(x+1, y).type == self.get_chip(x-1, y).type ):
                return True

        # 左方向2連
        if self.get_chip(x-1, y).type == self.get_chip(x-2, y).type :
            if (self.get_chip(x-1, y).type == self.get_chip(x, y-1).type or
                self.get_chip(x-1, y).type == self.get_chip(x, y+1).type or
                self.get_chip(x-1, y).type == self.get_chip(x+1, y).type ):
                return True

        # 上方向2連
        if self.get_chip(x, y-1).type == self.get_chip(x, y-2).type :
            if (self.get_chip(x, y-1).type == self.get_chip(x-1, y).type or
                self.get_chip(x, y-1).type == self.get_chip(x+1, y).type or
                self.get_chip(x, y-1).type == self.get_chip(x, y+1).type ):
                return True

        # 下方向2連
        if self.get_chip(x, y+1).type == self.get_chip(x, y+2).type :
            if (self.get_chip(x, y+1).type == self.get_chip(x-1, y).type or
                self.get_chip(x, y+1).type == self.get_chip(x+1, y).type or
                self.get_chip(x, y+1).type == self.get_chip(x, y-1).type ):
                return True

        # 縦カンチャン
        if self.get_chip(x, y-1).type == self.get_chip(x, y+1).type :
            if (self.get_chip(x, y-1).type == self.get_chip(x-1, y).type or
                self.get_chip(x, y-1).type == self.get_chip(x+1, y).type ) :
                return True

        # 横カンチャン
        if self.get_chip(x-1, y).type == self.get_chip(x+1, y).type :
            if (self.get_chip(x-1, y).type == self.get_chip(x, y-1).type or
                self.get_chip(x-1, y).type == self.get_chip(x, y+1).type ) :
                return True


        return False


    def check_tenpai_all(self):
        count = 0
        for y in range(App.BOX_HEIGHT) :
            for x in range(App.BOX_WIDTH) :
                if self.check_tenpai(x, y) :
                    self.box[x][y].tenpai = True
                    count += 1
                else :
                    self.box[x][y].tenpai = False
        return count

    def check_match(self):
        matched = False
        # 横チェック
        for y in range(App.BOX_HEIGHT) :
            for x in range(App.BOX_WIDTH-2) :
                if self.box[x][y].type == self.box[x+1][y].type == self.box[x+2][y].type :
                    self.box[x][y].match = self.box[x+1][y].match = self.box[x+2][y].match = True
                    matched = True

        # 縦チェック
        for x in range(App.BOX_WIDTH) :
            for y in range(App.BOX_HEIGHT - 2) :
                if self.box[x][y].type == self.box[x][y+1].type == self.box[x][y+2].type :
                    self.box[x][y].match = self.box[x][y+1].match = self.box[x][y+2].match = True
                    matched = True

        return matched

    def get_drag_chip(self) :
        return self.box[self.drag.x][self.drag.y]

    def get_drag2_chip(self) :
        return self.box[self.drag2.x][self.drag2.y]

    def draw_box(self):
        pyxel.rect(self.x2posx(0), self.y2posy(0), self.BOX_WIDTH*App.CHIP_SIZE, self.BOX_HEIGHT*App.CHIP_SIZE, 0)
        for x in range(App.BOX_WIDTH) :
            for y in range(App.BOX_HEIGHT) :
                if self.box[x][y] is None :
                    pass
                else :
                    self.box[x][y].draw()


    def delete_chips(self) :
        count =0
        for x in range(App.BOX_WIDTH):
            for y in range(App.BOX_HEIGHT-1,-1,-1):
                if self.box[x][y].match :
                    self.box[x][y] = None
                    count+=1
        return count

    def drop_chips(self) :
        for x in range(App.BOX_WIDTH):
            for y in range(App.BOX_HEIGHT-1, -1 ,-1):   # 下から上に処理
                if self.box[x][y] is None :
                    for i in range(y-1, -1, -1) :
                        if self.box[x][i] is not None :
                            self.box[x][y] = self.box[x][i]
                            self.box[x][y].set_dst(self.x2posx(x), self.y2posy(y))
                            self.box[x][i] = None
                            break

    def is_dropped_all(self) :
        for x in range(App.BOX_WIDTH):
            for y in range(App.BOX_HEIGHT-1, -1 ,-1):   # 下から上に処理
                if self.box[x][y] is not None and not self.box[x][y].is_dropped() :
                    return False

        return True

    def is_moved_all(self) :
        for x in range(App.BOX_WIDTH):
            for y in range(App.BOX_HEIGHT):
                if self.box[x][y] is not None and not self.box[x][y].is_moved() :
                    return False

        return True

    def refill_chips(self) :
        for x in range(App.BOX_WIDTH):
            for y in range(App.BOX_HEIGHT):
                if self.box[x][y] is None:
                    self.box[x][y] = Chip(self.x2posx(x), self.y2posy(y-1), pyxel.rndi(1, self.max_type), self.x2posx(x), self.y2posy(y))

    def is_release(self):
        return self.drag == self.drag2

    def is_swapable(self):
        swapable = [(0, 1), (0, -1), (1, 0), (-1, 0)]

        if self.get_drag_chip().type == self.get_drag2_chip().type :
            return False

        dx = self.drag2.x - self.drag.x
        dy = self.drag2.y - self.drag.y

        if (dx, dy) in swapable :
            return True
        else :
            return False

    def calc_score(self, count):
        # score =(count-2) * 100 * (self.combo+1)
        score =(count-2) * 100  + self.combo * 200
        return score

    def update_score(self, count):
        Debug.delete_count += count
        add_score = self.calc_score(count)
        self.score += add_score
        self.set_top_extra_text(f"+ {add_score}")
        self.add_timer_action(self.clear_top_extra_text, 6)
        Debug.print(f"count = {count}, combo = {self.combo}, add = {add_score}")

        self.se.get_score(self.combo)

    def set_top_text(self, text, color) :
        self.top_text = text
        self.top_text_color = color

    def set_top_text_to_score(self) :
        self.set_top_text(f"Score {self.score:08}", 7)

    def set_center_texts(self, texts, color) :
        self.center_texts = texts
        self.center_text_color = color

    def extend_center_texts(self, texts) :
        self.center_texts.extend(texts)

    def clear_center_text(self) :
        self.center_text = []

    def set_center_text_color(self, col) :
        self.center_text_color = col

    def draw_center_texts(self, start_y):
        mid_x = App.SCREEN_WIDTH // 2

        for i, text in enumerate(self.center_texts):
            x = mid_x - (len(text) * 2)
            y = start_y + (i * 8)
            pyxel.text(x, y, text, self.center_text_color)

    def set_top_extra_text(self, text) :
        self.top_extra_text = text

    def clear_top_extra_text(self) :
        self.top_extra_text = ""

    def draw_score(self):
        pyxel.text(App.CHIP_SIZE, 4, self.top_text, self.top_text_color)

    def draw_top_extra_text(self):
        pyxel.text(App.SCREEN_WIDTH/2 + 4, 4, self.top_extra_text, self.top_extra_text_color)

    def add_timer_action(self, func, delay) :
        self.timer_action_table[func] = pyxel.frame_count + delay

    def timer_action(self) :
        exec = []
        for func, frame in self.timer_action_table.items() :
            if pyxel.frame_count > frame :
                func()
                exec.append(func)

        for func in exec :
            del self.timer_action_table[func]

    def debug_output(self) :
        for x in range(App.BOX_WIDTH):
            for y in range(App.BOX_HEIGHT):
                if self.box[x][y] is None :
                    print(f"{x}, {y} is None")
                else :
                    print(f"{x}, {y} is {self.box[x][y].type}, x={self.box[x][y].pos_x}, y={self.box[x][y].pos_y}")


    def draw_title_box(self) :
        for col in range(1,9) :
            pyxel.blt(8 + (col-1)*App.CHIP_SIZE, 120, 0, col*App.CHIP_SIZE, 16, App.CHIP_SIZE, App.CHIP_SIZE, 0)

    def next_state(self, state, delay=0) :
        self.state = state
        self.set_counter(delay)

    def func_title(self) :
        text = ["Match3 Puzzle",
                "",
                "Click to start"]
        self.set_center_texts(text, 7)

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self.next_state(State.START)

    def func_start(self) :
        self.init_game()
        self.next_state(State.SELECT)

    def func_select(self):
        self.set_top_text_to_score()
        self.combo = 0

        if self.is_gameover() :
            self.next_state(State.GAMEOVER)

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if self.click_in_box() :
                if self.drag is None :
                    self.SelectChip(self.pos2boxidx(pyxel.mouse_x, pyxel.mouse_y))
                else :
                    self.SelectChip2(self.pos2boxidx(pyxel.mouse_x, pyxel.mouse_y))
                    if self.is_release() :
                        self.release_chip()
                    elif self.is_swapable() :
                        self.se.swap()
                        self.swap_chip()
                        self.next_state(State.CHECK1, 6)
                    else :
                        self.se.bad()
                        self.release_chip()

        self.update_game_timer()


    def func_check1(self):
        if self.is_expire() :
            if self.check_match() :
                self.next_state(State.DELETE, 4)
            else :
                self.se.undo_swap()
                self.undo_swap()
                self.next_state(State.SELECT)

    def func_delete(self) :
        if self.is_expire() :
            count = self.delete_chips()
            self.update_score(count)
            self.extend_game_timer(count)
            self.next_state(State.DROPDOWN, 9)

    def func_check2(self) :
        self.set_top_text_to_score()
        self.combo +=1
        if self.check_match() :
            self.next_state(State.DELETE, 9)
        else :
            self.next_state(State.CHECK_TENPAI)

    def func_dropdown(self) :
        if self.is_expire() :
            self.drop_chips()
            self.next_state(State.REFILL, 3)

    def func_refill(self) :
        if self.is_expire() and self.is_dropped_all() :
            self.refill_chips()
            self.next_state(State.WAIT_DROPPED_ALL, 3)

    def func_wait_dropped_all(self) :
        if self.is_expire() and self.is_dropped_all() :
            self.next_state(State.CHECK2)

    def func_check_tenpai(self) :
        if self.check_tenpai_all() > 0 :
            self.next_state(State.SELECT)
        else :
            self.next_state(State.NO_MORE_MOVE, 30)

    def func_no_more_move(self) :
        self.set_center_texts(["No more move"], 7)
        for x in range(App.BOX_WIDTH):
            for y in range(App.BOX_HEIGHT):
                self.box[x][y].dst_y = App.SCREEN_HEIGHT
                self.box[x][y].set_update_delta(6)
        if self.is_expire() :
            self.init_box()
            self.next_state(State.SELECT)

    def func_gameover(self) :
        pyxel.stop()
        self.se.gameover()
        for x in range(App.BOX_WIDTH):
            for y in range(App.BOX_HEIGHT):
                self.box[x][y].dst_y = App.SCREEN_HEIGHT
                self.box[x][y].set_update_delta(6)

        self.set_center_texts(["Game Over"], 8)
        self.next_state(State.WAIT_RESTART, 5*App.FPS)

    def func_wait_restart(self) :
        if self.is_expire():
            self.set_center_texts(["Game Over","", "Click to restart"], 8)
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                self.next_state(State.START)

    def update(self):

        if DEBUG :
            if pyxel.btnp(pyxel.KEY_D):
                self.debug_output()

            if pyxel.btnp(pyxel.KEY_P) :
                self.se.test_play_start = True
            self.se.test_play()

            # if pyxel.btnp(pyxel.KEY_R) :
            #     self.next_state(State.NO_MORE_MOVE, 30)

        self.gage.update(self.game_timer_val / (App.FPS * App.GAME_TIME))

        state_func = {
            State.TITLE : self.func_title,
            State.START : self.func_start,
            State.SELECT : self.func_select,
            State.CHECK1 : self.func_check1,
            State.DELETE: self.func_delete,
            State.CHECK2 : self.func_check2,
            State.DROPDOWN : self.func_dropdown,
            State.REFILL : self.func_refill,
            State.WAIT_DROPPED_ALL : self.func_wait_dropped_all,
            State.CHECK_TENPAI : self.func_check_tenpai,
            State.NO_MORE_MOVE : self.func_no_more_move,
            State.GAMEOVER : self.func_gameover,
            State.WAIT_RESTART : self.func_wait_restart,
        }[self.state]
        state_func()

        self.timer_action()
        self.update_counter()

    def draw(self):
        pyxel.cls(self.bg)
        self.draw_bg()

        if self.state == State.TITLE :
            self.draw_center_texts(App.SCREEN_HEIGHT//2 - 16)
            self.draw_title_box()
        elif self.state == State.NO_MORE_MOVE:
            self.draw_box()
            self.gage.draw()
            self.draw_center_texts(App.SCREEN_HEIGHT//2 - 16)
            self.draw_score()
        elif self.state == State.WAIT_RESTART :
            self.draw_box()
            self.draw_center_texts(App.SCREEN_HEIGHT//2 -16)
            self.draw_score()
        else :
            self.draw_box()
            self.gage.draw()
            self.draw_score()
            self.draw_top_extra_text()

            # debug
            if DEBUG :
                pyxel.text(160, 60, f"drag = {self.get_drag_chip().type if self.drag is not None else 0}", 7)
                pyxel.text(160, 70, f"state = {self.state}", 7)
                pyxel.text(160, 80, f"count = {self.down_counter}", 7)
                pyxel.text(160, 90, f"drop = {self.is_dropped_all()}", 7)
                pyxel.text(160, 100, f"game_timer = {self.game_timer_val}", 7)

App()


