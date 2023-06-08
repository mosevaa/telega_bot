from aiogram import Router
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from pyrogram import Client


router = Router()


class Order(StatesGroup):
    api_id = State()
    api_hash = State()
    number = State()
    code = State()


def make_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyborad=True)


@router.message(Command('start_join'))
async def set_api_id(message: Message, state: FSMContext):
    await message.answer(
        text='Введите api_id',
    )
    await state.set_state(Order.api_id)


@router.message(
    Order.api_id,
)
async def set_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_id=message.text)
    print(message.text)
    await message.answer(text='Далее введите api_hash')
    await state.set_state(Order.api_hash)


@router.message(
    Order.api_hash,
)
async def set_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_hash=message.text)
    print(message.text)
    await message.answer(text='Далее введите номер телефона')
    await state.set_state(Order.number)


@router.message(
    Order.number,
)
async def set_api_hash(message: Message, state: FSMContext):
    await state.update_data(number=message.text)
    user_data = await state.get_data()
    await message.answer(
        text=f'Введены следующие данные:\n'
             f'API_ID: {user_data["api_id"]}\n'
             f'API_HASH: {user_data["api_hash"]}\n'
             f'Номер телефона: {user_data["number"]}'
    )
    await state.set_state(Order.code)


@router.message(
    Order.code,
)
async def set_api_hash(message: Message, state: FSMContext):
    user_data = await state.get_data()
    app = Client('bot', api_id=user_data['api_id'], api_hash=user_data['api_hash'])
    app.send_code(user_data['number'])
    app.sign_in()
