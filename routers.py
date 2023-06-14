from aiogram import Router, F
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, Message
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext

from pyrogram import Client
from pyrogram.types import User

from functional import join

router = Router()


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:

    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True, one_time_keyboard=True)


available_answers = ['Да', 'Нет']
start_button = ['Начать']
return_button = ['Назад']
log_out_button = ['Выйти из аккаунта']


class Order(StatesGroup):
    api_id = State()
    api_hash = State()
    number = State()
    code = State()
    auth = State()
    urls_list = State()


@router.message(Command(commands=['start']))
async def start_function(message: Message):
    await message.answer(
        text='Добро пожаловать в бот!\n'
        'Нажмите кнопку Начать для того, чтобы добавить аккаунт в требуемые чаты.\n',
        reply_markup=make_row_keyboard(start_button)
    )


@router.message(Text(text='Начать', ignore_case=True))
async def set_api_id(message: Message, state: FSMContext):
    await message.answer(
        text='Введите api_id',
        reply_markup=make_row_keyboard(return_button)
    )
    await state.set_state(Order.api_id)


@router.message(Text(text="Выйти из аккаунта", ignore_case=True))
async def log_out(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text='Вы вернулись на главную',
                         reply_markup=make_row_keyboard(start_button))


@router.message(Text(text='Назад', ignore_case=True))
async def set_api_id(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text='Вы вернулись на главную',
        reply_markup=make_row_keyboard(start_button)
    )


@router.message(Text(text='Нет', ignore_case=True))
async def set_api_id(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text='Нажмите Начать, чтобы начать заново',
        reply_markup=make_row_keyboard(start_button)
    )


@router.message(
    Order.api_id,
)
async def set_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_id=message.text)
    print(message.text)
    await message.answer(
        text='Далее введите api_hash',
        reply_markup=make_row_keyboard(return_button)
    )
    await state.set_state(Order.api_hash)


@router.message(
    Order.api_hash,
)
async def set_api_hash(message: Message, state: FSMContext):
    await state.update_data(api_hash=message.text)
    print(message.text)
    await message.answer(
        text='Далее введите номер телефона',
        reply_markup=make_row_keyboard(return_button)
    )
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
             f'Номер телефона: {user_data["number"]}\n'
             f'Все верно?',
        reply_markup=make_row_keyboard(available_answers)
    )
    await state.set_state(Order.code)


@router.message(
    Order.code,
    F.text == 'Да'
)
async def set_api_hash(message: Message, state: FSMContext):
    user_data = await state.get_data()
    app = Client('bot', api_id=user_data['api_id'], api_hash=user_data['api_hash'])
    await app.connect()
    sent_code = await app.send_code(user_data['number'])
    await state.update_data(code_hash=sent_code.phone_code_hash, app=app)
    await message.answer(text='Введите код подтверждения')
    await state.set_state(Order.auth)


@router.message(
    Order.auth
)
async def get_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text)
    user_data = await state.get_data()
    app = user_data['app']
    code = message.text
    try:
        signed_in = await app.sign_in(
            phone_number=user_data['number'],
            phone_code_hash=user_data['code_hash'],
            phone_code=code
        )
        if isinstance(signed_in, User):
            print('successful')
        await message.answer(
            text='Введите ссылки групп, в которые нужно вступить.\n'
                 'Каждую ссылку вводите в новой строке\n'
                 'Все ссылки должны находиться в одном сообщении.'
        )
    except Exception as e:
        print(e)
    await state.set_state(Order.urls_list)


@router.message(
    Order.urls_list
)
async def set_url(message: Message, state: FSMContext):
    user_data = await state.get_data()
    urls = message.text
    urls = urls.split('\n')
    await message.answer(
        text=f'Всего введено {len(urls)} ссылок\n'
            'Начинаю вступать. Как только закончу, придет соответствующее сообщение.'
    )
    await join(urls, user_data['app'])
    await message.answer(
        text='Готово!',
        reply_markup=make_row_keyboard(start_button)
    )




