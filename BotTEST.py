# -*- coding: utf-8 -*-
import json
import uuid
from yookassa import Configuration, Payment

from Parser import get_html
import random
from aiogram.utils.helper import Helper, HelperMode, ListItem
import Config #Config.py файл с токенами и др.
#Весь бот
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
#Указываем память
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
#Состояния
from States import States
from aiogram.dispatcher import FSMContext
#БД
from Sqlitert import Members
#Почта
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
num = 1

class ContentType(Helper):
    """
    List of message content types

    :key: TEXT
    :key: AUDIO
    :key: DOCUMENT
    :key: GAME
    :key: PHOTO
    :key: STICKER
    :key: VIDEO
    :key: VOICE
    :key: NEW_CHAT_MEMBERS
    :key: LEFT_CHAT_MEMBER
    :key: INVOICE
    :key: SUCCESSFUL_PAYMENT
    :key: UNKNOWN
    """
    mode = HelperMode.snake_case

    TEXT = ListItem()  # text
    AUDIO = ListItem()  # audio
    DOCUMENT = ListItem()  # document
    GAME = ListItem()  # game
    PHOTO = ListItem()  # photo
    STICKER = ListItem()  # sticker
    VIDEO = ListItem()  # video
    VOICE = ListItem()  # voice
    NEW_CHAT_MEMBERS = ListItem()  # new_chat_members
    LEFT_CHAT_MEMBER = ListItem()  # left_chat_member
    INVOICE = ListItem()  # invoice
    SUCCESSFUL_PAYMENT = ListItem()



Members = Members('Main.db')

bot = Bot(Config.TOKEN, parse_mode=types.ParseMode.MARKDOWN)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

citys = ['Москва', 'Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Нижний Новгород', 'Казань', 'Самара', 'Челябинск', 'Омск', 'Ростов-на-Дону']


@dp.message_handler(commands=['switch'])
async def switch(message: types.Message):
    if message.from_user.id == Config.ADMIN:
        await get_state(message, 10)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    Members.test()
    if Members.check_registration(message.from_user.id):
        await main_menu(message)
    else:
        await message.answer('*⭕️Для начала пройди регистрацию*')
        await get_state(message, 1)

@dp.message_handler(commands=['forcemajeure'])
async def forcemajeure(message: types.Message):
    await message.answer('*©Правила©*\n\n_Как и в любом деле бывают форс мажоры\n\n'
                         '- Если в друг в твой город мы не сможем организовать доставку , то мы готовы либо выкупить такой же товар у реселлера рядом с тобой либо перевести средства!\n\n'
                         '-Возможны задержки по доставке , но тут больше беда в транспортной компании либо почте!\n\n'
                         '-Доставка в страны СНГ не включает в себя доставку!\n\n'
                         '-И всегда помни, что любую ситуацию легко исправить и мы всегда это готовы решить!_\n\n\n'
                         '*С уважением TEHART✊*')

@dp.message_handler()
async def echo_message(message: types.Message):
    msg = message.text
    print(msg)
    print(Config.YOOTOKEN)
    print(message.from_user.id)
    if msg == 'Профиль 👤':
        await get_profile(message)

    if msg == 'Магазины 🏬':
        await message.answer('*Отправьете ссылку на товар из этого магазина и мы ответим есть ли этот товар у нас в наличии:\n\n👉 https://m.re-store.ru\n\n👉 https://www.technopark.ru*',parse_mode='Markdown', disable_web_page_preview=True)

    elif msg == 'О нас ℹ️':
        await message.answer('*🚛Мы занимаемся поставкой техники любых брендов (*_Apple, samsung, xiaomi и т.д_*)\n'
                             '💁🏽‍♂️Благодаря сотруднечеству с поставщиками в реселлеры мы можем предлагать вам технику дешевле именитых магазинов\n'
                             '📶 Мы работаем не ради большой наживы на продаже, а на качество и объемы продаж\n'
                             '🤑Также некоторые товары мы берем по системе кешбека и тем самым мы можем его предлагать дешевле!\n'
                             '📱Ведь лучше продать 100 iphone с наценкой 2000р чем продавать их дешевле реселлеров на 2000р и не кому их не продать?!\n'
                             '🏪 Поэтому мы создали этот магазин для вас и всегда готовы привезти вам ваши любимые девайсы*')
    elif msg == 'Инструкции ⚒':
        await message.answer('*🛍Как заказать товар?🛍*\n_- В меню в разделе магазины вы можете перейти по ссылке\n'
                             '- Выбрать тот товар который вам необходим\n'
                             '- Скинуть ссылку нашему боту\n'
                             '- Бот выдаст вам предложения цены\n'
                             '- Выбери предложенные сроки поставки_\n\n'
                             '*🧐Как происходит оплата?🧐*\n'
                             '_✔️Вы выбрали для себя удобный вариант доставки и готовы оплатить.\n'
                             '✔️Для этого вы переходите по кнопке оплата и переноситесь в окно оплаты\n'
                             '✔️Как только вы оплатили вам придет подтверждение и в ближайшее время с вами свяжется наш менеджер для подтверждения и уточнения способа и адреса доставки._')

    if 'https:' in msg:
        await message.answer('_Ожидайте, получаем информацию о товаре..._', parse_mode='Markdown')

        info = await get_html(msg)
        print(info)
        await get_order(message, info)


async def get_state(message, arg):
    if arg == 1:
        await bot.send_message(message.chat.id, '*✉️ Введи свой e-mail*')
        await States.Mail.set()
    elif arg == 2:
        rkm = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for city in citys:
            rkm.add(city)
        await bot.send_message(message.chat.id, '*🏙 Введи свой город, или выбери из предложенных*', reply_markup=rkm)
        await States.City.set()
    elif arg == 3:
        rkm = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Пропустить')
        await bot.send_message(message.chat.id, '*📱 Укажи номер телефона*', reply_markup=rkm)
        await States.Phone.set()
    elif arg == 4:
        rkm = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена')

        await bot.send_message(message.chat.id, '*📱 Укажи номер телефона*', reply_markup=rkm)
        await States.EnterPhone.set()

    elif arg == 10:
        rkm = types.ReplyKeyboardMarkup(resize_keyboard=True).add('Отмена')

        await bot.send_message(message.chat.id, '*Введи токен*', reply_markup=rkm)
        await States.EnterPhone.set()

@dp.message_handler(state=States.EnterPhone)
async def token(message: types.Message, state: FSMContext):
    token = message.text
    if token == 'Отмена':
        await state.reset_state(with_data=True)
        await main_menu(message)
    else:
        Config.YOOTOKEN = token
        await state.reset_state(with_data=True)
        print(Config.YOOTOKEN)
        await main_menu(message)


@dp.message_handler(state=States.Mail)
async def get_mail(message: types.Message, state: FSMContext):
    msg = message.text
    if message.text == '/start':
        await state.reset_data(with_data=True)
        await start(message)
    else:
        if '@' in msg and '.' in msg and len(msg) > 4:
            mass = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P']
            num = 0
            code = []
            while num < 5:
                code.append(random.choice(mass))
                num += 1
            code = ''.join(code)

            await state.update_data(
                {code:msg}
            )
            await mail(message.text, code)
            await message.answer('🔐 На твой e-mail пришёл код, введи его')
            await States.Code.set()
        else:
            await message.answer('*Введи корректный адрес*')


@dp.message_handler(state=States.Code)
async def get_code(message: types.Message, state: FSMContext):
    print(message.text)
    if message.text == '/start':
        await start(message)
    else:
        data = await state.get_data()
        print(data)
        try:

            code = data[message.text]
            print(code + '=====')
            if code:
                await state.update_data({
                    'mail':code
                })
                await get_state(message, 2)

        except:
            await message.answer('Неверный код, проверьте и попробуйте снова.\nПрезагрузка бота /start')


async def mail(user_mail, code):
    from platform import python_version
    subject = 'Registration'
    body = f'Your registration code:\n======\n{code}\n======'

    email_text = """\
    From: %s
    To: %s
    Subject: %s

    %s
    """ % ('tehartshop@gmail.com', user_mail, subject, body)
    mail = Config.MAIL
    mail_password = Config.MAIL_PASSWORD
    smtpObj = smtplib.SMTP('smtp.gmail.com', 587)
    smtpObj.starttls()
    smtpObj.login(mail, mail_password)
    smtpObj.sendmail(mail, user_mail, email_text)

@dp.message_handler(state=States.City)
async def get_city(message: types.Message, state: FSMContext):
    city = message.text
    if isinstance(city, str):
        await state.update_data(
            {
                'town':city
            }
        )
        await get_state(message, 3)
    else:
        message.answer('*Проверьте город*')


@dp.message_handler(state=States.Phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.text
    if phone == 'Пропустить':
        await state.update_data({
            'phone': None
        })
        data = await state.get_data()
        await state.reset_state(with_data=True)

        await registration(data=data,message=message)
    else:
        if len(phone) >= 4 and phone[1:].isdigit():
            await state.update_data({
                'phone':phone
            })
            data = await state.get_data()
            await state.reset_state(with_data=True)
            await registration(data, message)


@dp.message_handler(state=States.EnterPhone)
async def EnterPhone(message: types.Message, state: FSMContext):
    phone = message.text
    if phone == 'Отмена':
        await state.reset_state(with_data=True)
        await main_menu(message)
    if len(phone) >= 4 and phone[1:].isdigit():
        Members.update_phone(message.from_user.id, phone)
        await state.reset_state(with_data=True)
        await main_menu(message)
    else:
        await message.answer('*Введи корректный номер*')


async def registration(data, message):
    Members.registration(message.from_user.id, message.from_user.username, data['mail'], data['phone'], data['town'])
    await message.answer('*👏Регистрация пройдена !👏*')
    await main_menu(message)


async def main_menu(message):
    kbm = types.ReplyKeyboardMarkup(resize_keyboard=True)

    profile = 'Профиль 👤'
    shops = 'Магазины 🏬'
    about = 'О нас ℹ️'
    manual = 'Инструкции ⚒'

    kbm.add(profile).add(shops).add(about, manual)
    await message.answer('*- Жми на раздел “*_МАГАЗИН_*”\n- Выбери товар на сайте\n- Скинь ссылку в чат\n- Бот рассчитает предложения на твой товар*', reply_markup=kbm)


async def get_profile(message):
    info = Members.get_profile(message.from_user.id)
    print(info)
    if info[4]:
        try:
            textM = f'👤 _@{message.from_user.username}_\n\n*🆔 Your ID: {info[1]}\n\n📬 Mail: {info[3]}\n\n☎️ Phone: {info[4]}\n\n🏙 City: {info[-1]}*'
            await message.answer(textM)
        except:
            text = f'👤 @{message.from_user.username}\n\n🆔 Your ID: {info[1]}\n\n📬 Mail: {info[3]}\n\n☎️ Phone: {info[4]}\n\n🏙 City: {info[-1]}'
            await message.answer(text, parse_mode='HTML')
    else:
        ikm = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton(text='Ввести номер', callback_data='enter_phone'))

        try:
            textM = f'👤 _@{message.from_user.username}_\n\n*🆔 Your ID: {info[1]}\n\n📬 Mail: {info[3]}\n\n☎️ Phone: Not entered\n\n🏙 City: {info[-1]}*'
            await message.answer(textM, reply_markup=ikm)
        except:
            text = f'👤 @{message.from_user.username}\n\n🆔 Your ID: {info[1]}\n\n📬 Mail: {info[3]}\n\n☎️ Phone: {info[4]}\n\n🏙 City: {info[-1]}'
            await message.answer(text, parse_mode='HTML', reply_markup=ikm)


async def redirect_to_order(params, text,chat_id):
    payment_url = params[0]
    payment_id = params[1]
    print(len(payment_id))
    kbm = types.InlineKeyboardMarkup()

    pay = types.InlineKeyboardButton(text='Оплатить', url=payment_url)
    chek_pay = types.InlineKeyboardButton(text='Проверить платёж', callback_data=f'chekpay_{payment_id}')
    kbm.add(pay).add(chek_pay)

    await bot.send_message(chat_id, text, reply_markup=kbm)


async def chek_pay(payment_id):
    Configuration.account_id = 834629
    Configuration.secret_key = Config.YOOTOKEN
    payment = Payment.find_one(payment_id).json()
    p_dict = json.loads(payment.replace("'", '"'))
    return p_dict['paid']


async def get_order(message, info):
    name = info['product_name']
    price = info['product_price']
    float_price = float(''.join(price.split()))
    discount_10 = int(float_price) - float_price / 100 * 10
    discount_20 = int(float_price) - float_price / 100 * 20
    discount_30 = int(float_price) - float_price / 100 * 30
    discount_50 = int(float_price) - float_price / 100 * 50
    ikm = types.InlineKeyboardMarkup()

    print(len(name))
    print('data')
    data = len(f'10_{name}_{price}')
    try:
        if data>=41:
            ten = types.InlineKeyboardButton(text=f'{discount_10}₽ - 14 дней', callback_data=f'10_{name[:-20]}_{price}')
            twenty = types.InlineKeyboardButton(text=f'{discount_20}₽ - 21 день', callback_data=f'20_{name[:-20]}_{price}')
            thirty = types.InlineKeyboardButton(text=f'{discount_30}₽ - 28 дней', callback_data=f'30_{name[:-20]}_{price}')
            fifty = types.InlineKeyboardButton(text=f'{discount_50}₽ - 45 дней', callback_data=f'50_{name[:-20]}_{price}')
            ikm.add(ten).add(twenty).add(thirty).add(fifty)
        else:
            ten = types.InlineKeyboardButton(text=f'{discount_10}₽ - 14 дней', callback_data=f'10_{name}_{price}')
            twenty = types.InlineKeyboardButton(text=f'{discount_20}₽ - 21 день', callback_data=f'20_{name}_{price}')
            thirty = types.InlineKeyboardButton(text=f'{discount_30}₽ - 28 дней', callback_data=f'30_{name}_{price}')
            fifty = types.InlineKeyboardButton(text=f'{discount_50}₽ - 45 дней', callback_data=f'50_{name}_{price}')
            ikm.add(ten).add(twenty).add(thirty).add(fifty)

        try:
            await message.answer(f'*Наименование товара:* _{name}_\n*Стоимость товара на сайте:* _{price}₽_\n\n_Выберите стоимость и срок доставки _', parse_mode='Markdown', reply_markup=ikm)
        except:
            await message.answer(f'Наименование товара: {name}\nСтоимость товара на сайте: {price}₽\n\nВыберите стоимость и срок доставки', reply_markup=ikm)
    except:
        await message.answer('*К сожалению не удалось составить предложение для вас, попробуйте другой товар*')
@dp.callback_query_handler()
async def call_back(call: types.CallbackQuery):
    print(call.data)
    data = call.data
    if len(data.split('_'))==3:
        if data[:2].isdigit():
            product_info = data.split('_')
            discount = int(product_info[0])
            product_name = product_info[1]
            product_price = float(''.join(product_info[2].split()))

            product_price_with_discount = int((product_price - product_price / 100 * discount))

            params = await create_order(description=f'{product_name}\nПокупка со скидкой {discount}%', prices=product_price_with_discount)
            text = f'*Покупка <*_{product_name}_*> со скидкой {discount}%\nСтоимость товара с учётом скидки: {product_price_with_discount}₽\nCтоимость товара в магазине: {product_price}₽*\n\n_После проведения оплаты нажмите "Проверить платёж"_'
            await redirect_to_order(params, text, call.message.chat.id)


    if data.startswith('chekpay'):
        is_pay = await chek_pay(data.split('_')[-1])
        if is_pay == True:

            await call.message.answer('*✅ Оплата прошла успешно\n😌 Ожидайте, с вами свяжется наш менеджер*')
            print(call.message.chat.id)
            user_info = Members.get_profile(call.message.chat.id)
            print(user_info)
            product_info = await chek_product_info(data.split('_')[-1])
            await bot.send_message(Config.ADMIN, f'*ЗАКАЗ\n\nИнформация о пользователе:\nuser_name: @{user_info[2]}\n'
                                                 f'Почта: {user_info[3]}\n'
                                                 f'Номер телефона: {user_info[4]}\n'
                                                 f'Город: {user_info[-1]}\n'
                                                 f'{product_info}*')

            await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, None)
        else:
            await call.message.answer('*➖ Оплата не найдена*')

    if data == 'enter_phone':
        await get_state(call.message, 4)


async def chek_product_info(payment_id):
    Configuration.account_id = 834629
    Configuration.secret_key = Config.YOOTOKEN
    payment = Payment.find_one(payment_id).json()
    p_dict = json.loads(payment.replace("'", '"'))
    return p_dict['description']


async def create_order(description, prices):
    Configuration.account_id = 834629
    Configuration.secret_key = Config.YOOTOKEN


    payment = Payment.create({
        "amount": {
            "value": f"{prices}.00",
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://www.merchant-website.com/return_url"
        },
        "capture": True,
        "description": f"Заказ\n{description}"
    }, uuid.uuid4())

    p_json = payment.json()
    p_dict = json.loads(p_json.replace("'", '"'))
    confirmation_url = p_dict['confirmation']['confirmation_url']
    payment_id = p_dict['id']
    print(payment_id)

    return confirmation_url, payment_id


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
