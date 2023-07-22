from vkbottle import Keyboard, Text, KeyboardButtonColor

class KBDManager:
    start_keyboard = (
        Keyboard(one_time=False, inline=False)
        .row()
        .add(Text("/search"), color=KeyboardButtonColor.POSITIVE)
        )

    stop_search_k = (
        Keyboard(one_time=False, inline=False)
        .row()
        .add(Text(label="/stop_search"), color=KeyboardButtonColor.PRIMARY)
        )

    stop_dialog_k = (
        Keyboard(one_time=False, inline=False)
        .row()
        .add(Text(label="/stop_dialog"),color=KeyboardButtonColor.NEGATIVE)
        )