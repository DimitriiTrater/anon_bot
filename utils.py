from vkbottle.bot import Message
from kbd_manager import Keyboard
from usr_bot import bot


async def check_can_write(user_id: int) -> bool:
    conversation = await bot.api.messages.get_conversations_by_id([user_id])
    can_write = conversation.items[0].can_write.allowed
    return can_write


async def send_text(user_id_out: int,
                    message_in: str,
                    keyboard: Keyboard = Keyboard()
                    ):
    await bot.api.messages.send(
        peer_id=user_id_out,
        random_id=0,
        message=message_in,
        keyboard=keyboard
    )


async def send_message(user_id_out: int,
                       message_in: Message
                       ):
    await bot.api.messages.send(
        peer_id=user_id_out,
        random_id=0,
        message="Собеседник: " + message_in.text,
    )

    await send_attachments(user_id_out, message_in)


async def send_attachments(user_id_out: int, message_in: Message) -> int:
    if not message_in.attachments:
        return 1

    for attachment in message_in.attachments:
        # for stickers
        # it has a problem if stiker is not available now
        if (attachment.sticker):
            await bot.api.messages.send(
                peer_id=user_id_out,
                random_id=0,
                sticker_id=attachment.sticker.sticker_id
            )
            return 0

        # other attachments
        attachment = await get_attachment(attachment)
        await bot.api.messages.send(
            peer_id=user_id_out,
            random_id=0,
            attachment=attachment
        )
    return 0


# only for video, audio and photo
# when i send the doc it said me that it deleted
# idk what the reason is
async def get_attachment(attachment) -> str:
    type_str = attachment.type.value
    owner_id = eval(f"attachment.{type_str}.owner_id")
    media_id = eval(f"attachment.{type_str}.id")
    acs_tok = eval(f"attachment.{type_str}.access_key")
    return f"{type_str}{owner_id}_{media_id}_{acs_tok}"
