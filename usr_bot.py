from vkbottle.bot import Bot
from typing import List, Dict, TypeVar
from api import api

usr_id = TypeVar("usr_id", bound=int)


class App():
    def __init__(self) -> None:
        self.wait_list: List[usr_id] = []
        self.dialogs_dict: Dict[usr_id, usr_id] = {}

    def get_size_of_wait_list(self) -> int:
        return len(self.wait_list)

    def get_size_of_users_in_dialog(self) -> int:
        return round(len(self.dialogs_dict)/2)


app = App()
bot = Bot(api=api)
