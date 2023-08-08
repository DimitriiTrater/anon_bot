from api import api
from typing import List, Dict, TypeVar
from kbd_manager import KBDManager, Keyboard
from vkbottle.bot import Bot, Message
from consts import CONSTS

bot = Bot(api=api)

wait:    List[int] = []
dialogs: Dict[int, int] = {}


@bot.on.message(text="Большой брат бдит")
async def big_brother(message: Message):
    if not await check_can_write(message.from_id):
        return

    await message.answer(
        f"Здравствуйте, великий! \nКоличество диалогов: {len(dialogs)}.\nЛюдей в очереди: {len(wait)}"
    )


@bot.on.message(text="Начать")
async def hi_handler(message: Message):
    if not await check_can_write(message.from_id):
        return

    user_info = await bot.api.users.get(message.from_id)
    await message.answer(
        f"Привет, {user_info[0].first_name}.\n Чтобы начать поиск напиши \'/search\' или ткни на кнопку.",
        keyboard=KBDManager.start_keyboard
    )


@bot.on.message(text="/search")
async def search(message: Message):
    user_id = message.from_id
    if not await check_can_write(user_id):
        return

    if user_id in wait or user_id in dialogs:
        return

    if not wait:
        await message.answer("В очереди.", keyboard=KBDManager.stop_search_k)
        wait.append(user_id)
        return

    first_in_queue = wait[0]
    del wait[0]

    dialogs[user_id] = first_in_queue
    dialogs[first_in_queue] = user_id

    await bot.api.messages.send(
        peer_id=user_id,
        random_id=0,
        message="Мы нашли вам собеседника!",
        keyboard=KBDManager.stop_dialog_k
    )

    if not await check_can_write(first_in_queue):
        del dialogs[user_id]
        del dialogs[first_in_queue]
        await bot.api.messages.send(
            peer_id=user_id,
            random_id=0,
            message="Собеседник запретил писать ему сообщения.\nНачните поиск снова.",
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

    if message.from_id not in wait:
        await message.answer("Вы не в очереди!",
                             keyboard=KBDManager.start_keyboard)
        return

    del wait[wait.index(message.from_id)]
    await message.answer("Вы остановили поиск.",
                         keyboard=KBDManager.start_keyboard)


@bot.on.message(text="/stop_dialog")
async def stop_dialog(message: Message):
    first_usr:  int = message.from_id

    if not await check_can_write(first_usr):
        return

    if first_usr not in dialogs:
        await message.answer("У вас нет собеседника!",
                             keyboard=KBDManager.start_keyboard)
        return

    second_usr: int = dialogs[first_usr]

    del dialogs[first_usr]
    del dialogs[second_usr]

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

    if first_usr in wait:
        await message.answer(
            "Вы уже ищите собеседника!\n/stop_search - отменить поиск",
            keyboard=KBDManager.stop_search_k
        )
        return

    if first_usr not in wait and first_usr not in dialogs:
        await message.answer(
            "Привет, используй кнопку.",
            keyboard=KBDManager.start_keyboard
        )
        return

    if first_usr in wait and first_usr in dialogs:
        del dialogs[first_usr]
        del wait[wait.index(first_usr)]
        return

    if first_usr in dialogs:
        second_usr = dialogs[first_usr]
        if await check_can_write(second_usr):
            await send_message(second_usr, message)
            return

        del dialogs[first_usr]
        del dialogs[second_usr]
        await send_message(first_usr, CONSTS.STRING.FORBIDDEN, KBDManager.start_keyboard)


async def check_can_write(user_id: int) -> bool:
    conversation = await bot.api.messages.get_conversations_by_id([user_id])
    can_write = conversation.items[0].can_write.allowed
    return can_write


async def send_message(user_id_out: int,
                       message_in: Message,
                       keyboard: Keyboard = Keyboard()
                       ):
    await bot.api.messages.send(
        peer_id=user_id_out,
        random_id=0,
        message="Собеседник: " + message_in.text,
    )
    print("DEBUGING: " + str(len(message_in.attachments)))

    await send_attachments(user_id_out, message_in)


async def send_attachments(user_id_out: int, message_in: Message) -> int:
    print("SEND_ATTACHMENTS FUNCTION")

    if not message_in.attachments[0]:
        return 1

    print("ATTACHEMNTS HAS")

    for attachment in message_in.attachments:
        t = await get_attachment(attachment)
        print("Before sending attachment")
        await bot.api.messages.send(
            peer_id=user_id_out,
            random_id=0,
            attachment=str(t)
        )
        print("After sending attachment")
    return 0


async def get_attachment(attachment) -> str:
    type_str = attachment.type.value
    owner_id = eval(f"attachment.{type_str}.owner_id")
    media_id = eval(f"attachment.{type_str}.id")
    acs_tok = eval(f"attachment.{type_str}.access_key")
    return f"{type_str}{owner_id}_{media_id}_{acs_tok}"
    

if __name__ == "__main__":
    bot.run_forever()
