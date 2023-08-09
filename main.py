from kbd_manager import KBDManager
from utils import check_can_write
from utils import send_message, send_text
from consts import CONSTS
from usr_bot import app, bot
from vkbottle.bot import Message


@bot.on.message(text="Большой брат бдит")
async def big_brother(message: Message):
    if not await check_can_write(message.from_id):
        return

    await message.answer(
        f"""Здравствуйте, великий!
        \nКоличество диалогов: {app.get_size_of_users_in_dialog()}.
        \nЛюдей в очереди: {app.get_size_of_wait_list()}"""
    )


@bot.on.message(text="Начать")
async def hi_handler(message: Message):
    if not await check_can_write(message.from_id):
        return

    user_info = await bot.api.users.get(message.from_id)
    await message.answer(
        f"""Привет, {user_info[0].first_name}.\n
        Чтобы начать поиск напиши \'/search\' или ткни на кнопку.""",
        keyboard=KBDManager.start_keyboard
    )


@bot.on.message(text="/search")
async def search(message: Message):
    user_id = message.from_id
    if not await check_can_write(user_id):
        return

    if user_id in app.wait_list or user_id in app.dialogs_dict:
        return

    if not app.wait_list:
        await message.answer("В очереди.", keyboard=KBDManager.stop_search_k)
        app.wait_list.append(user_id)
        return

    first_in_queue = app.wait_list[0]
    del app.wait_list[0]

    app.dialogs_dict[user_id] = first_in_queue
    app.dialogs_dict[first_in_queue] = user_id

    await bot.api.messages.send(
        peer_id=user_id,
        random_id=0,
        message="Мы нашли вам собеседника!",
        keyboard=KBDManager.stop_dialog_k
    )

    if not await check_can_write(first_in_queue):
        del app.dialogs_dict[user_id]
        del app.dialogs_dict[first_in_queue]
        await bot.api.messages.send(
            peer_id=user_id,
            random_id=0,
            message=CONSTS.STRING.FORBIDDEN,
            keyboard=KBDManager.start_keyboard
        )
        return

    await bot.api.messages.send(
        peer_id=first_in_queue,
        random_id=0,
        message="Мы нашли вам собеседника!",
        keyboard=KBDManager.stop_dialog_k
    )


@bot.on.message(text="/stop_search")
async def stop_search(message: Message):
    if not await check_can_write(message.from_id):
        return

    if message.from_id not in app.wait_list:
        await message.answer("Вы не в очереди!",
                             keyboard=KBDManager.start_keyboard)
        return

    del app.wait_list[app.wait_list.index(message.from_id)]
    await message.answer("Вы остановили поиск.",
                         keyboard=KBDManager.start_keyboard)


@bot.on.message(text="/stop_dialog")
async def stop_dialog(message: Message):
    first_usr:  int = message.from_id

    if not await check_can_write(first_usr):
        return

    if first_usr not in app.dialogs_dict:
        await message.answer("У вас нет собеседника!",
                             keyboard=KBDManager.start_keyboard)
        return

    second_usr: int = app.dialogs_dict[first_usr]

    del app.dialogs_dict[first_usr]
    del app.dialogs_dict[second_usr]

    await bot.api.messages.send(
        peer_id=first_usr,
        random_id=0,
        message="Диалог был остановлен.",
        keyboard=KBDManager.start_keyboard
    )

    if not await check_can_write(second_usr):
        return

    await bot.api.messages.send(
        peer_id=second_usr,
        random_id=0,
        message="Собеседник остановил диалог.",
        keyboard=KBDManager.start_keyboard
    )


@bot.on.message()
async def all(message: Message):
    first_usr = message.from_id
    if not await check_can_write(first_usr):
        return

    if first_usr in app.wait_list:
        await message.answer(
            "Вы уже ищите собеседника!\n/stop_search - отменить поиск",
            keyboard=KBDManager.stop_search_k
        )
        return

    if first_usr not in app.wait_list and first_usr not in app.dialogs_dict:
        await message.answer(
            "Привет, используй кнопку.",
            keyboard=KBDManager.start_keyboard
        )
        return

    if first_usr in app.wait_list and first_usr in app.dialogs_dict:
        del app.dialogs_dict[first_usr]
        del app.wait_list[app.wait_list.index(first_usr)]
        return

    if first_usr in app.dialogs_dict:
        second_usr = app.dialogs_dict[first_usr]
        if await check_can_write(second_usr):
            await send_message(second_usr, message)
            return

        del app.dialogs_dict[first_usr]
        del app.dialogs_dict[second_usr]
        await send_text(user_id_out=first_usr,
                        message_in=CONSTS.STRING.FORBIDDEN,
                        keyboard=KBDManager.start_keyboard)

if __name__ == "__main__":
    bot.run_forever()
