import asyncio
import types

from api import api
from typing import List, Dict
from kbd_manager import KBDManager
from vkbottle.bot import Bot, Message
from vkbottle import VKAPIError

bot = Bot(api=api)

wait:    List[int]      = []
dialogs: Dict[int, int] = {}


@bot.on.message(text="Большой брат бдит")
async def big_brother(message: Message):
    if not await check_can_write(message.from_id): return;
    
    await message.answer(
        f"Здравствуйте, великий! \nКоличество диалогов: {len(dialogs)}.\nЛюдей в очереди: {len(wait)}"
    )


@bot.on.message(text="Начать")
async def hi_handler(message: Message):
    if not await check_can_write(message.from_id): return;

    user_info = await bot.api.users.get(message.from_id)
    await message.answer(
        f"Привет, {user_info[0].first_name}.\n Чтобы начать поиск напиши \'/search\' или ткни на кнопку.",
        keyboard=KBDManager.start_keyboard
    )


@bot.on.message(text="/search")
async def search(message: Message):
    user_id = message.from_id
    if not await check_can_write(user_id): return;

    if user_id in wait or user_id in dialogs:
        return;

    if not wait:
        await message.answer("В очереди.", keyboard=KBDManager.stop_search_k)
        wait.append(user_id)
        return;
    
    first_in_queue = wait[0]
    del wait[0]
    
    dialogs[user_id] = first_in_queue
    dialogs[first_in_queue] = user_id

    await bot.api.messages.send(
        peer_id=user_id,
        random_id=0,
        message='Мы нашли вам собеседника!',
        keyboard=KBDManager.stop_dialog_k
    )

    if not await check_can_write(first_in_queue): 
        del dialogs[user_id]
        del dialogs[first_in_queue]
        await bot.api.messages.send(
            peer_id=user_id,
            random_id=0,
            message='Собеседник запретил писать ему сообщения.\nНачните поиск снова.',
            keyboard=KBDManager.start_keyboard
        )   
        return;

    await bot.api.messages.send(
        peer_id=first_in_queue,
        random_id=0,
        message='Мы нашли вам собеседника!',
        keyboard=KBDManager.stop_dialog_k
    )


@bot.on.message(text="/stop_search")
async def stop_search(message: Message):
    if not await check_can_write(message.from_id): return;

    if message.from_id not in wait:
        await message.answer('Вы не в очереди!', keyboard=KBDManager.start_keyboard)
        return;
    
    del wait[wait.index(message.from_id)]
    await message.answer('Вы остановили поиск.', keyboard=KBDManager.start_keyboard)


@bot.on.message(text="/stop_dialog")
async def stop_dialog(message: Message):
    first_usr:  int = message.from_id
    second_usr: int = dialogs[first_usr]

    if not await check_can_write(first_usr): return;

    if first_usr not in dialogs:
        await message.answer('У вас нет собеседника!', keyboard=KBDManager.start_keyboard)
        return;

    del dialogs[first_usr]
    del dialogs[second_usr]

    await bot.api.messages.send(
        peer_id=first_usr,
        random_id=0,
        message='Диалог был остановлен.',
        keyboard=KBDManager.start_keyboard
    )
    
    if not await check_can_write(second_usr): return;
    
    await bot.api.messages.send(
        peer_id=second_usr,
        random_id=0,
        message='Собеседник остановил диалог.',
        keyboard=KBDManager.start_keyboard
    )



@bot.on.message()
async def all(message: Message):
    if message.from_id in wait:
        await message.answer(
            'Вы уже ищите собеседника! \n /stop_search - отменить поиск',
            keyboard=KBDManager.stop_search_k)
    if message.from_id not in wait and message.from_id not in dialogs:
        await message.answer(
            'Привет, используй кнопку. Если тебе вылезло это сообщение, то скорее всего ты не в очереди ожидания и не в диалоге. Если ты не начинал поиск и не был в диалоге, то всё хорошо, просто начинай поиск. Но если ты был в очереди/диалоге, то проверь разрешил ли ты отправлять группе сообщения. Если всё в порядке, то скорее всего проблема у нас и мы о ней уже знаем и пытаемся исправить. Попробуй начать поиск сначала.',
            keyboard=KBDManager.start_keyboard
        )
    try:
        if message.from_id in dialogs:
            await bot.api.messages.send(peer_id=dialogs[message.from_id], random_id=0, message='Собеседник: ' + message.text)
    except VKAPIError[901]:
        try:
            await bot.api.messages.send(
                peer_id=message.from_id,
                random_id=0,
                message='Собеседник запретил отправлять ему сообщения, диалог остановлен.',
                keyboard=start_keyboard
                )
        except VKAPIError[901]:
            await bot.api.messages.send(
                peer_id=dialogs[message.from_id],
                random_id=0,
                message='Собеседник запретил отправлять ему сообщения, диалог остановлен.',
                keyboard=KBDManager.start_keyboard
                )
        del dialogs[dialogs[message.from_id]]
        del dialogs[message.from_id]



async def check_can_write(user_id: int) -> bool:
    conversation = await bot.api.messages.get_conversations_by_id([user_id])
    can_write = conversation.items[0].can_write.allowed
    return can_write


if __name__ == "__main__":
    bot.run_forever()