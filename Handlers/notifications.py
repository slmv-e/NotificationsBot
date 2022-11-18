import vk_api
import time
import datetime as dt
from scheduler import Scheduler
from vk_api.longpoll import VkLongPoll
from vk_api.utils import get_random_id
from Handlers.parser import get_message_data
from Handlers.json_h import read_from_json


class Notifications:
    def __init__(self, login, password, token, group_token):
        self.login = login
        self.password = password
        self.token = token
        self.vk_session = vk_api.VkApi(token=group_token)
        self.session_api = self.vk_session.get_api()
        self.longpoll = VkLongPoll(self.vk_session)

    def handler(self):
        message_data = get_message_data(self.login, self.password, self.token)
        message_text = "Актуальные данные:\n\n"
        for i, message_data_slice in enumerate(message_data):
            message_text += f"{message_data_slice['lesson_name']}\n" \
                            f"➥ Количество работ: {message_data_slice['works_cnt']}\n"
            if i != len(message_data) - 1:
                message_text += "---------------------------\n"
        users_list = read_from_json()["USER_LIST"]
        for user_id in users_list:
            try:
                self.session_api.messages.send(peer_id=user_id, message=message_text, random_id=get_random_id())
            except Exception as ex:
                print(ex)

    def start(self):
        schedule = Scheduler(tzinfo=dt.timezone.utc)
        tz_moscow = dt.timezone(dt.timedelta(hours=3))
        for hour in [0, *range(10, 24)]:
            schedule.daily(dt.time(hour=hour, tzinfo=tz_moscow), self.handler)
        while True:
            schedule.exec_jobs()
            time.sleep(1)
