from enum import Enum, auto
import functools

class CommonState(Enum):
    WAIT_ON_START = auto()
    WAIT_INPUT_PHONE = auto()
    WAIT_INPUT_CODE = auto()

class EditSenderState(Enum):
    WAIT_COMMAND = auto()
    WAIT_INPUT_PARAM = auto()
    WAIT_INPUT_RECIEVER = auto() 
    WAIT_SEND_FINISH = auto()    

class EditBotState(Enum):
    WAIT_COMMAND = auto()
    WAIT_INPUT_PARAM = auto()


class FSM:
    def __init__(self):
        self.state = {}
        self.data = {}
    def get_state(self, who: int):
        return self.state.get(who)
    def set_state(self, who: int, state):
        self.state[who] = state
    def get_data(self, who: int):
        data = self.data.get(who)
        return data if data else {}
    def set_data(self, who: int, data):
        self.data[who] = data


def allowed_states(states):
    def actual_decorator(func):
        @functools.wraps(func)
        async def wrapper(event):
            who = event.sender_id
            state = fsm.get_state(who)
            if ((type(states) == list and state in states) or 
                (state == None) or
                (type(states) != list and state == states)):
                return await func(event, who)
            else:
                return 
        return wrapper                
    return actual_decorator

fsm = FSM()    