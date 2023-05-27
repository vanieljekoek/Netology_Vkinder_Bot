# Import required libraries and modules from VK lib
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

keyboard = VkKeyboard(one_time=False)
keyboard.add_button('Привет', color=VkKeyboardColor.POSITIVE)
keyboard.add_line()
keyboard.add_button('Поиск', color=VkKeyboardColor.SECONDARY)
keyboard.add_line()
keyboard.add_button('Следующие', color=VkKeyboardColor.PRIMARY)
keyboard.add_line()
keyboard.add_button('Пока', color=VkKeyboardColor.NEGATIVE)