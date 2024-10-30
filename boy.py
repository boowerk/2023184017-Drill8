from turtledemo.sorting_animate import start_isort

from pico2d import load_image, get_time
from pygame.display import update

from state_machine import StateMachine, space_down, time_out, right_down, left_up, left_down, right_up, start_event, \
    a_down


# 상태를 클래스를 통해서 정의함.
class Idle:
    @staticmethod   # 그 뒤에 이어서 오는 함수는 staticmethod 함수로 간주함
    def enter(boy, e):
        if left_up(e) or right_down(e):
            boy.action = 2
            boy.face_dir = -1
        elif right_up(e) or left_down(e) or start_event(e):
            boy.action = 3
            boy.face_dir = 1

        boy.dir = 0 # 정지 상태이다.
        boy.frame = 0
        # 현재 시간을 저장
        boy.start_time = get_time()
        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        if get_time() - boy.start_time > 3:
            boy.state_machine.add_event(('TIME_OUT', 0))
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(boy.frame * 100, boy.action * 100, 100, 100, boy.x, boy.y)
        pass

class Sleep:
    @staticmethod
    def enter(boy, e):

        pass

    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.frame = (boy.frame + 1) % 8
        pass

    @staticmethod
    def draw(boy):
        if boy.face_dir == 1:   # 오른쪽 바라보는 상태에 눕기
            boy.image.clip_composite_draw(
                boy.frame * 100, 300, 100, 100,
                3.141592 / 2, # 90 도 회전
                '', # 좌우상하 반전 X, H = 좌우 반전, V = 상하 반전
                boy.x - 25, boy.y - 25, 100, 100
            )
        elif boy.face_dir == -1:
            boy.image.clip_composite_draw(
                boy.frame * 100, 200, 100, 100,
                -3.141592 / 2,  # 90 도 회전
                '',  # 좌우상하 반전 X, H = 좌우 반전, V = 상하 반전
                boy.x + 25, boy.y - 25, 100, 100
            )
        pass

class Run:
    @staticmethod
    def enter(boy, e):
        if right_down(e) or left_up(e):
            boy.dir = 1
            boy.action = 1
        elif left_down(e) or right_up(e):
            boy.dir = -1
            boy.action = 0
        boy.frame = 0
    @staticmethod
    def exit(boy, e):
        pass

    @staticmethod
    def do(boy):
        boy.x += boy.dir * 5
        boy.frame = (boy.frame + 1) % 8

    @staticmethod
    def draw(boy):
        boy.image.clip_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            boy.x, boy.y
        )

class AutoRun:
    @staticmethod
    def enter(boy, e):
        boy.dir = 1 if boy.face_dir == 1 else -1
        boy.autorun_time = get_time()
        boy.action = 1 if boy.dir == 1 else 0
        boy.size = 100
        pass

    @staticmethod
    def exit(boy, e):
        boy.action = 2
        pass

    @staticmethod
    def do(boy):
        boy.x += boy.dir * 30
        boy.frame = (boy.frame + 1) % 8
        if boy.x < 0 or boy.x > 800:
            boy.dir *= -1
            boy.face_dir = boy.dir

            if boy.action == 1:
                boy.action = 0
            elif boy.action == 0:
                boy.action = 1

        if get_time() - boy.autorun_time > 5:
            boy.state_machine.add_event(('TIME_OUT', 0))
        pass

    @staticmethod
    def draw(boy):
        boy.image.clip_composite_draw(
            boy.frame * 100, boy.action * 100, 100, 100,
            0, '',  # 회전 없음
            boy.x, boy.y, boy.size, boy.size  # 크기 적용
        )
        pass


class Boy:
    def __init__(self):
        self.x, self.y = 400, 90
        self.frame = 0
        self.dir = 0
        self.action = 3
        self.image = load_image('animation_sheet.png')
        self.state_machine = StateMachine(self) # 소년 객체의 state machine 생성
        self.state_machine.start(Idle)      # 초기 상태가 Idle
        self.state_machine.set_transitions(
            {
                Idle: {right_down: Run, left_down: Run, left_up: Run, right_up: Run, a_down: AutoRun,time_out: Sleep},
                Run: {right_down: Idle, left_down: Idle, right_up: Idle, left_up: Idle},
                Sleep: {right_down: Run, left_down: Run, right_up: Run, left_up: Run, space_down: Idle},
                AutoRun: {right_down: Run, left_down: Run, right_up: Run, left_up:Run, time_out: Idle}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        # event : 입력 이벤트 key mouse
        # 우리가 state machine 전달해줄건 (    ,    )
        self.state_machine.add_event(
            ('INPUT', event)
        )

    def draw(self):
        self.state_machine.draw()

