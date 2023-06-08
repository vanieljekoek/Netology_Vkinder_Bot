from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def create_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button('Поиск', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Следующие', color=VkKeyboardColor.SECONDARY)
    keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)
    return keyboard
