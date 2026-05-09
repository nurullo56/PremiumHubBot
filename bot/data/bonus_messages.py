# bot/data/bonus_messages.py
from dataclasses import dataclass
from typing import List
import random

@dataclass
class BonusMessage:
    emoji: str
    text: str

BONUS_TEMPLATES: List[BonusMessage] = [
    BonusMessage("🎉", "Yangi bonus!\n\n👤 {fullname} ro'yxatdan o'tdi!\n💎 +1.4 olmos hisobingizga qo'shildi!\n\nDavom eting! 🚀"),
    BonusMessage("✨", "Ajoyib yangilik!\n\n🎯 {fullname} qo'shildi!\n💰 +1.4 olmos sizniki!\n\nOldinga! 🔥"),
    BonusMessage("🎊", "Tabriklaymiz!\n\n👥 {fullname} jamoangizda!\n💎 +1.4 olmos mukofot!\n\nYutishda davom eting! ⚡"),
    BonusMessage("🌟", "Zo'r natija!\n\n🎪 {fullname} start oldi!\n💵 +1.4 olmos qo'shildi!\n\nMuvaffaqiyatlar! 🎯"),
    BonusMessage("🎁", "Yangi sovg'a!\n\n🆕 {fullname} a'zo bo'ldi!\n💎 +1.4 olmos hisobda!\n\nBoshing! 🚀"),
    BonusMessage("🔥", "Ajoyib!\n\n👤 {fullname} sizga qo'shildi!\n💰 +1.4 olmos bonus!\n\nYutuqlar sari! 🎉"),
    BonusMessage("⭐", "Yangi yutuq!\n\n🎭 {fullname} ishga tushdi!\n💎 +1.4 olmos olgansiz!\n\nDavom eting! 💪"),
    BonusMessage("🎈", "Mukofot!\n\n👨‍💼 {fullname} ro'yxatda!\n💵 +1.4 olmos taqdim etildi!\n\nOldinga! 🚀"),
    BonusMessage("💫", "Zo'r yangilik!\n\n🎪 {fullname} qo'shildi!\n💎 +1.4 olmos sizda!\n\nMuvaffaqiyat! 🎯"),
    BonusMessage("🎆", "Bayram!\n\n👥 {fullname} jamoada!\n💰 +1.4 olmos bonus!\n\nUddalaysiz! 🔥"),
    BonusMessage("🌈", "Qutlaymiz!\n\n🎯 {fullname} start oldi!\n💎 +1.4 olmos mukofot!\n\nYutishda davom! ⚡"),
    BonusMessage("🎪", "Ajoyib ish!\n\n🆕 {fullname} a'zo!\n💵 +1.4 olmos hisobda!\n\nOldinga qadam! 🚀"),
    BonusMessage("🏆", "Yangi g'alaba!\n\n👤 {fullname} sizniki!\n💎 +1.4 olmos qo'shildi!\n\nDavom eting! 🎉"),
    BonusMessage("💥", "Zo'r!\n\n🎭 {fullname} qo'shildi!\n💰 +1.4 olmos bonus!\n\nYutuqlar kutmoqda! 🔥"),
    BonusMessage("🎀", "Tabrik!\n\n👨‍💼 {fullname} ro'yxatdan o'tdi!\n💎 +1.4 olmos sizda!\n\nMuvaffaqiyatlar! 🎯"),
    BonusMessage("🌠", "Yangi natija!\n\n🎪 {fullname} jamoada!\n💵 +1.4 olmos mukofot!\n\nBoshing! 🚀"),
    BonusMessage("🎵", "Ajoyib yangilik!\n\n👥 {fullname} qo'shildi!\n💎 +1.4 olmos hisobingizda!\n\nDavom eting! ⚡"),
    BonusMessage("🎨", "Zo'r ish!\n\n🎯 {fullname} ishga tushdi!\n💰 +1.4 olmos bonus!\n\nOldinga! 🔥"),
    BonusMessage("🎬", "Yangi bonus!\n\n🆕 {fullname} a'zo bo'ldi!\n💎 +1.4 olmos taqdim!\n\nYutishda davom! 🎉"),
    BonusMessage("🎤", "Mukofot!\n\n👤 {fullname} ro'yxatda!\n💵 +1.4 olmos sizniki!\n\nUddalaysiz! 💪"),
    BonusMessage("🎧", "Ajoyib!\n\n🎭 {fullname} qo'shildi!\n💎 +1.4 olmos hisobda!\n\nMuvaffaqiyat! 🎯"),
    BonusMessage("🎸", "Yangi yutuq!\n\n👨‍💼 {fullname} jamoangizda!\n💰 +1.4 olmos bonus!\n\nBoshing! 🚀"),
    BonusMessage("🎹", "Tabriklaymiz!\n\n🎪 {fullname} start oldi!\n💎 +1.4 olmos mukofot!\n\nDavom eting! ⚡"),
    BonusMessage("🎺", "Zo'r natija!\n\n👥 {fullname} sizga qo'shildi!\n💵 +1.4 olmos qo'shildi!\n\nOldinga qadam! 🔥"),
    BonusMessage("Violin", "Qutlaymiz!\n\n🎯 {fullname} a'zo!\n💎 +1.4 olmos hisobingizda!\n\nYutuqlar sari! 🎉"),
    BonusMessage("🥁", "Yangi sovg'a!\n\n🆕 {fullname} ro'yxatdan o'tdi!\n💰 +1.4 olmos sizda!\n\nDavom eting! 💪"),
    BonusMessage("🎲", "Ajoyib ish!\n\n👤 {fullname} ishga tushdi!\n💎 +1.4 olmos bonus!\n\nMuvaffaqiyatlar! 🎯"),
    BonusMessage("🎰", "Zo'r!\n\n🎭 {fullname} qo'shildi!\n💵 +1.4 olmas taqdim!\n\nOldinga! 🚀"),
    BonusMessage("🎮", "Yangi bonus!\n\n👨‍💼 {fullname} jamoada!\n💎 +1.4 olmos mukofot!\n\nBoshing! ⚡"),
    BonusMessage("🎯", "Mukofot!\n\n🎪 {fullname} ro'yxatda!\n💰 +1.4 olmos hisobda!\n\nUddalaysiz! 🔥"),
    BonusMessage("🎳", "Tabrik!\n\n👥 {fullname} sizniki!\n💎 +1.4 olmos qo'shildi!\n\nDavom eting! 🎉"),
    BonusMessage("🎪", "Ajoyib yangilik!\n\n🎯 {fullname} qo'shildi!\n💵 +1.4 olmos bonus!\n\nYutishda davom! 💪"),
    BonusMessage("🎢", "Yangi natija!\n\n🆕 {fullname} a'zo bo'ldi!\n💎 +1.4 olmos sizda!\n\nMuvaffaqiyat! 🎯"),
    BonusMessage("🎡", "Zo'r ish!\n\n👤 {fullname} start oldi!\n💰 +1.4 olmos hisobingizda!\n\nOldinga! 🚀"),
    BonusMessage("🎠", "Qutlaymiz!\n\n🎭 {fullname} ro'yxatdan o'tdi!\n💎 +1.4 olmos mukofot!\n\nBoshing! ⚡"),
    BonusMessage("🎏", "Yangi yutuq!\n\n👨‍💼 {fullname} jamoangizda!\n💵 +1.4 olmos bonus!\n\nDavom eting! 🔥"),
    BonusMessage("🎐", "Ajoyib!\n\n🎪 {fullname} qo'shildi!\n💎 +1.4 olmos taqdim!\n\nYutuqlar sari! 🎉"),
    BonusMessage("🎑", "Zo'r natija!\n\n👥 {fullname} ishga tushdi!\n💰 +1.4 olmos hisobda!\n\nOldinga qadam! 💪"),
    BonusMessage("🎇", "Yangi bonus!\n\n🎯 {fullname} a'zo!\n💎 +1.4 olmos sizniki!\n\nMuvaffaqiyatlar! 🎯"),
    BonusMessage("🎃", "Tabriklaymiz!\n\n🆕 {fullname} ro'yxatda!\n💵 +1.4 olmos qo'shildi!\n\nUddalaysiz! 🚀"),
]

def get_random_bonus_message(fullname: str) -> str:
    """Random bonus xabarini formatlab qaytarish."""
    template = random.choice(BONUS_TEMPLATES)
    # Emoji va formatlangan matnni birlashtiramiz
    return f"{template.emoji} {template.text.format(fullname=fullname)}"