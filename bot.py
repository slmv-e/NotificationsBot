from vkbottle.bot import Bot, Message
from vkbottle import API
from vkbottle.dispatch.rules import ABCRule
from typing import Tuple
from threading import Thread
from asyncio import run
from Handlers.json_h import read_from_json, dump_to_json
from Handlers.notifications import Notifications

gr_token = read_from_json()["GROUP_TOKEN"]
bot = Bot(token=gr_token)
api = API(token=gr_token)


class AdminRule(ABCRule[Message]):
    def __init__(self, admin_list: list):
        self.admin_list = admin_list

    async def check(self, event: Message) -> bool:
        return True if (await event.get_user(raw_mode=True))['id'] in self.admin_list else False


bot.labeler.custom_rules["admin_only"] = AdminRule


@bot.on.message(command=("exhelp", 0), admin_only=read_from_json()["ADMIN_LIST"])
async def help_(message: Message):
    await message.answer(f"Команды:\n\n"
                         f"/add_chat <id> - Добавить чат в список для рассылки\n"
                         f"/remove_user <id> - Удалить чат из списка для рассылки\n"
                         f"/add_admin <id> - Добавить администратора (администратор может использоватать команды, остальные - нет)\n"
                         f"/remove_admin <id> - Удалить администратора\n"
                         f"/list - Список чатов, куда приходит рассылка\n"
                         f"/admin_list - Список администраторов\n\n"
                         f"Примечание: вместо <id> вписать id чата (только число). Чтобы получить id чата напишите команду /show_chat_id\n"
                         f"P. S. Чтобы добавить пользователя, вместо <id> вписать id пользователя (только число)")


@bot.on.message(command=("add_chat", 1), admin_only=read_from_json()["ADMIN_LIST"])
async def add_chat_(message: Message, args: Tuple[str]):
    user_id = int(args[0])

    user_list = read_from_json()["USER_LIST"]
    if user_id not in user_list:
        user_list.append(user_id)
        dump_to_json(key="USER_LIST", value=user_list)
        await message.answer(f'Чат успешно добавлен')
    else:
        await message.answer(f'Чат уже есть в списке')


@bot.on.message(command=("list", 0), admin_only=read_from_json()["ADMIN_LIST"])
async def list_(message: Message):
    user_list = read_from_json()["USER_LIST"]
    if user_list:
        msg_text = "Список чатов, получающих уведомления:\n\n"
        for index, user_id in enumerate(user_list, 1):
            msg_text += f"{index}. {user_id}\n"
        await message.answer(msg_text)
    else:
        await message.answer("Список пуст...")


@bot.on.message(command=("remove_chat", 1), admin_only=read_from_json()["ADMIN_LIST"])
async def remove_chat_(message: Message, args: Tuple[str]):
    user_id = int(args[0])

    user_list = read_from_json()["USER_LIST"]
    if user_id in user_list:
        user_list.remove(user_id)
        dump_to_json(key="USER_LIST", value=user_list)
        await message.answer(f'Чат успешно удален из списка')
    else:
        await message.answer(f'Чат отсутствует в списке')


@bot.on.message(command=("add_admin", 1), admin_only=read_from_json()["ADMIN_LIST"])
async def add_admin_(message: Message, args: Tuple[str]):
    admin_id = int(args[0])
    user_get = dict((await api.users.get(user_ids=admin_id))[0])
    user_first_name = user_get['first_name']
    user_last_name = user_get['last_name']

    admin_list = read_from_json()["ADMIN_LIST"]
    if admin_id not in admin_list:
        admin_list.append(admin_id)
        dump_to_json(key="ADMIN_LIST", value=admin_list)
        await message.answer(f'{user_first_name} {user_last_name} успешно внесен в список администраторов')
    else:
        await message.answer(f'{user_first_name} {user_last_name} уже является администратором')


@bot.on.message(command=("admin_list", 0), admin_only=read_from_json()["ADMIN_LIST"])
async def admin_list_(message: Message):
    admin_list = read_from_json()["ADMIN_LIST"]
    if not admin_list:
        await message.answer("Список пуст...")
    else:
        msg_text = "Список администраторов:\n\n"
        for index, admin_id in enumerate(admin_list, 1):
            user_get = dict((await api.users.get(user_ids=admin_id))[0])
            user_first_name = user_get['first_name']
            user_last_name = user_get['last_name']
            msg_text += f"{index}. ID: {admin_id}\n" \
                        f"Имя администратора: {user_first_name} {user_last_name}\n\n"
        await message.answer(msg_text)


@bot.on.message(command=("remove_admin", 1), admin_only=read_from_json()["ADMIN_LIST"])
async def remove_admin_(message: Message, args: Tuple[str]):
    admin_id = int(args[0])
    user_get = dict((await api.users.get(user_ids=admin_id))[0])
    user_first_name = user_get['first_name']
    user_last_name = user_get['last_name']

    admin_list = read_from_json()["ADMIN_LIST"]
    if admin_id in admin_list:
        admin_list.remove(admin_id)
        dump_to_json(key="ADMIN_LIST", value=admin_list)
        await message.answer(f'{user_first_name} {user_last_name} успешно удален из списка администраторов')
    else:
        await message.answer(f'{user_first_name} {user_last_name} отсутствует в списке администраторов')


@bot.on.message(command=("show_chat_id", 0), admin_only=read_from_json()["ADMIN_LIST"])
async def add_current_chat_(message: Message):
    chat_id = message.peer_id
    await message.answer(f"ID чата: {chat_id}")


def main():
    data = read_from_json()
    login = data["AUTH_100POINTS"]["email"]
    password = data["AUTH_100POINTS"]["password"]
    vk_token = data["VK_TOKEN"]
    group_token = data["GROUP_TOKEN"]
    notif_app = Notifications(login, password, vk_token, group_token)

    notifications_process = Thread(target=notif_app.start)
    bot_process = Thread(target=run, args=(bot.run_polling(), ))

    notifications_process.start()
    bot_process.start()

    notifications_process.join()
    bot_process.join()


if __name__ == "__main__":
    main()
