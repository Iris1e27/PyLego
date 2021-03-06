# Copyright - Kiven, 2018
from pos_utils import *
import nxt.locator as locator
from nxt.motor import *
from threading import Thread
from nxt.sensor import *
from time import sleep
from threading import Thread
gb_bound = 20  # todo: adapt these two values
gw_bound = 39

print("PyLego initializing.")
print("Copyright - Kiven, 2018")

# initializing fields.
# P.S. *private* fields and functions begin with '_',
# they are not supposed to be invoked by any users (for details please google or baidu it)
# and the author will not be responsible for any mistakes caused by this

b = None
L = None
R = None
lmove = Thread()
rmove = Thread()
M = None
_lock = False
light = None
sonic = None
touch = None
guard_process = True
pos = Position()  # which marks the position of the robot
boxes = Boxes()  # which stores all the boxes here


_degree_to_spin_r = _to_rolls = \
{
    '90': 0.7,
    '45': 0.33,
    '30': 0.22,
    '-90': -0.7,
    '-45': -0.35,
    '-30': -0.233,
}


def _guard():
    pass


def to_cm(r):
    # this convert the roll param to centimeters
    if r < 15:  # todo: complete this
        r *= 360
    pass


def reset(remote=False):
    global b, L, R, M, lmove, rmove, _lock, light, sonic, touch
    print("Connecting")
    connect_method = locator.Method(not remote, remote)
    b = locator.find_one_brick(method=connect_method, debug=True)
    print("Connection to brick established\n")

    print("Initializing sensors")
    L = m_left = Motor(b, PORT_B)
    R = m_right = Motor(b, PORT_C)
    M = SynchronizedMotors(L, R, 2)
    lmove = Thread()
    rmove = Thread()
    _lock = False
    light = Light(b, PORT_3)
    sonic = Ultrasonic(b, PORT_2)
    touch = Touch(b, PORT_4)
    print("Initialization completed\n")
    print("Loading Actions")


if not b:
    try:
        reset()
    except:
        reset(True)

'''
def _handle_threads():
    def _do():
        global kill
        kill = True
        sleep(0.1)
        kill = False
    Thread(target=_do()).run()
'''


def l(r=1, p=75, t=None, b=True):  # changed the rule
    sleep(0.2)
    if r < 15:
        r *= 360
    L.turn(p, r, b)


def r(r=1, p=75, t=None, b=True):
    sleep(0.2)
    if r < 15:
        r *= 360
    R.turn(p, r, b)


right = r


def _l(r=1, p=100, t=None, b=True): # changed the rule
    if r < 15:  # todo: say this in the documentation
        r *= 360
    L.turn(p, r, b)


def _r(p=100, r=1, t=None, b=True):
    if r < 15:  # todo: say this in the documentation
        r *= 360
    R.turn(p, r, b)


def spin(r=1, p=75):
    sleep(0.2)
    global _lock
    if type(r) == str:
        pos.track(int(r), 0)
        r = _to_rolls[r]
    if r < 0:
        r, p = -r, -p
    if r < 15:
        r *= 360
    op1 = Thread(target=_locked(L.turn), args=(-p, r, False))
    op2 = Thread(target=_locked(R.turn), args=(p, r, False))
    op1.start()
    op2.start()
    while _lock:
        pass
    # print("exit turn")


def _locked(func):
    def output(*args):
        global _lock
        # print("locked")
        _lock = True
        func(*args)
        _lock = False
        # print("unlocked")
    return output


def hold_on():
    Thread(target=_locked(raw_input),
           args=("To end this hold-on, please enter anything: ",))\
        .start()
    global _lock
    while _lock:
        L.turn(1, 1)
        sleep(0.5)
        R.turn(1, 1)


def f(r=1, p=75, t=None):
    global lmove, rmove, _lock
    pos.track(0, to_cm(r))
    if not r or r==0:  # unlimited
        M.run(p)
    else:
        M.turn(p, r if r >= 15 else r*360, False)


def b(r=1, p=75, t=None):
    f(r, -p, t)


def _test():
    m = SynchronizedMotors(L, R, 0.5)
    m.turn(100, 360)


def stop():
    L.brake()
    R.brake()
    sleep(0.2)
    L.idle()
    R.idle()


def brightness():
    return light.get_lightness()


def distance():
    return sonic.get_distance()


def green():
    if gw_bound > brightness() > gb_bound:
        return True
    return False


def black():
    if brightness() < gb_bound:
        return True
    return False


def white():
    if brightness() > gw_bound:
        return True
    return False


def hit():
    return touch.is_pressed() or distance() < 5


def sound():
    Thread(target=b.play_tone_and_wait, args=(3, 1000)).start()
