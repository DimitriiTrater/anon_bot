from config import TOKEN
from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text, VKAPIError


bot = Bot(token=TOKEN)

wait = []
dialogs = {}

# start
start_keyboard = Keyboard(
    one_time=False,
    inline=False
    )
start_keyboard.row()
start_keyboard.add(
    Text(label="/search"),
    color=KeyboardButtonColor.POSITIVE)

# stop_search
stop_search_k = Keyboard(
    one_time=False,
    inline=False
    )
stop_search_k.row()
stop_search_k.add(
    Text(label="/stop_search"),
    color=KeyboardButtonColor.PRIMARY
    )

# stop_dialog
stop_dialog_k = Keyboard(
    one_time=False,
    inline=False
    )
stop_dialog_k.row()
stop_dialog_k.add(
    Text(label="/stop_dialog"),
    color=KeyboardButtonColor.NEGATIVE
    )


@bot.on.message(text="Большой брат бдит")
async def big_brother(message: Message):
    await message.answer(
        f"Здравствуйте, великий! \nКоличество диалогов: {len(dialogs)}.\nЛюдей в очереди: {len(wait)}"
    )

@bot.on.message(text="Начать")
async def hi_handler(message: Message):
    user_info = await bot.api.users.get(message.from_id)
    await message.answer(
        f"Привет, {user_info[0].first_name}.\n Чтобы начать поиск напиши \'/search\' или ткни на кнопку.",
        keyboard=start_keyboard
        )


@bot.on.message(text="/search")
async def search(message: Message):
    if message.from_id not in wait and message.from_id not in dialogs:
        if not wait:
            await message.answer(
                "Поиск, чтобы остановить поиск нажми на кнопку.",
                keyboard=stop_search_k
            )
            wait.append(message.from_id)
        else:
            dialogs[message.from_id] = wait[0]
            dialogs[wait[0]] = message.from_id
            await bot.api.messages.send(
                peer_id=message.from_id,
                random_id=0,
                message='Мы нашли вам собеседника!',
                keyboard=stop_dialog_k
            )
            await bot.api.messages.send(
                peer_id=wait[0],
                random_id=0,
                message='Мы нашли вам собеседника!',
                keyboard=stop_dialog_k
            )
            del wait[0]


@bot.on.message(text="/stop_search")
async def stop_search(message: Message):
    if message.from_id in wait:
        del wait[wait.index(message.from_id)]
        await message.answer('Вы остановили поиск.', keyboard=start_keyboard)
    else:
        await message.answer('Вы не в очереди!')


@bot.on.message(text="/stop_dialog")
async def stop_dialog(message: Message):
    if message.from_id in dialogs:
        await bot.api.messages.send(
            peer_id=message.from_id,
            random_id=0,
            message='Диалог был остановлен.',
            keyboard=start_keyboard
            )
        await bot.api.messages.send(
            peer_id=dialogs[message.from_id],
            random_id=0,
            message='Собеседник остановил диалог.',
            keyboard=start_keyboard
            )
        del dialogs[dialogs[message.from_id]]
        del dialogs[message.from_id]
    else:
        await message.answer('У вас нет собеседника!')


@bot.on.message()
async def all(message: Message):
    if message.from_id in wait:
        await message.answer(
            'Вы уже ищите собеседника! \n /stop_search - отменить поиск',
            keyboard=stop_search_k)
    if message.from_id not in wait and message.from_id not in dialogs:
        await message.answer(
            'Привет, используй кнопку. Если тебе вылезло это сообщение, то скорее всего ты не в очереди ожидания и не в диалоге. Если ты не начинал поиск и не был в диалоге, то всё хорошо, просто начинай поиск. Но если ты был в очереди/диалоге, то проверь разрешил ли ты отправлять группе сообщения. Если всё в порядке, то скорее всего проблема у нас и мы о ней уже знаем и пытаемся исправить. Попробуй начать поиск сначала.',
            keyboard=start_keyboard
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
                keyboard=start_keyboard
                )
        del dialogs[dialogs[message.from_id]]
        del dialogs[message.from_id]

bot.run_forever()
