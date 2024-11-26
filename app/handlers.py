import io
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from PIL import Image
from aiogram.types import FSInputFile, BufferedInputFile
from app.generators import generate
import app.keyboards as kb
import os
from dotenv import load_dotenv
from io import BytesIO
import numpy as np

load_dotenv()

router = Router()

#state
class Req(StatesGroup):
  art = State()
  filter_to_search = State()
  message_to_recommend = State()

class Color(StatesGroup):
  message_to_get_color = State()
  message_with_color_response = State()

class Res(StatesGroup):
  message_with_response = State()
    
#helpers
def get_choice_in_art(s): 
  return 'музыку' if s == 'Музыка' else 'фильмы' if s == 'Фильмы' else 'книги'

def get_choice_in_filter_to_search(s):
  #'Песня,Исполнитель,Альбом,Жанр,Книга,Писатель,Фильм,Режиссёр'
  if s == 'Исполнитель':
    return 'Исполнителя'
  if s == 'Песня':
    return 'песни'
  if s == 'Альбом':
    return 'альбома'
  if s == 'Жанр':
    return 'жанра'
  if s == 'Книга':
    return 'книги'
  if s == 'Писатель':
    return 'писателя'
  if s == 'Фильм':
    return 'фильма'
  if s == 'Режиссёр':
    return 'режиссёра'

def get_choice_in_ending(s): 
  return 'ую' if s == 'Музыка' else 'ие'

word_in_filter_choice = {
        'Жанр': 'название жанра',
        'Исполнитель': 'имя музыкального исполнителя',
        'Альбом': 'название альбома',
        'Песня': 'название песни',
        'Книга': 'название книги',
        'Писатель': 'имя писателя',
        'Фильм': 'название фильма',
        'Режиссёр': 'имя режиссёра'
    }


#message_handlers

@router.message(Command('start'))
async def on_start(message: Message):
  await message.reply('Привет! Здесь ты можешь на основе твоих предпочтений в музыке, книгах, фильмах получить рекомендацию от нейросети или уникальный увет своего вкуса!', reply_markup=kb.reply)


@router.message((F.text == 'Получить рекомендацию') | (F.text == '/get_recommendation'))
async def get_recommendation(message: Message, state: FSMContext):
  await state.clear()
  await state.set_state(Req.art)
  await message.reply('По чему ты хочешь получить рекомендацию?', reply_markup=await kb.create_inline_keyboard(os.getenv('inline_with_all_arts').split(',')))
    
@router.message((F.text == 'Узнать цвет своего вкуса') | (F.text == '/get_unique_color'))
async def want_to_get_color(message: Message, state: FSMContext):
  await state.clear()
  await state.set_state(Color.message_to_get_color)
  await message.answer('Напиши свои любые фильмы/музыку/книги через запятую')
  
@router.message(Color.message_to_get_color)
async def get_arts_to_get_color(message: Message, state: FSMContext):
  loading_msg = ''
  try:
    await state.set_state(Color.message_with_color_response)
    loading_msg = await message.answer('Нейросеть отвечает на ваше сообщение...')
    res_with_color = await generate(f'Верни уникальный цвет вкуса пользователя в формате rgb (верни только 3 числа через запятую, больше ничего не отправляй!), учитывая его любимые фильмы, книги или музыку, которые даны в следующей строке через запятую: {message.text}. Учти, что книги или фильмы с жанром "Драма", "Мелодрама", грустная музыка делают цвет голубоватым (но не полностью голубым), а книги или фильмы с жанром "Боевик", "Триллер", "Ужасы", тяжелая музыка (металл, тяжёлый рок) делают цвет почти полностью ярко выраженным красным, а оптимистичные или весёлые книги, фильмы, музыка (семейные фильмы, комедии) делают цвет почти полностью желтым. Чем больше произведений, сопутсвующих данным условиям, чем ярче будет соответсвующий цвет. Делай цвета немного необычными, но не в коем случае не отклоняйся о  условий данных выше. ОТПРАВЬ ТОЛЬКО 3 ЧИСЛА ЧЕРЕЗ ЗАПЯТУЮ, БОЛЬШЕ НИЧЕГО НЕ ПИШИ. ОТПРАВЬ ТОЛЬКО 3 ЧИСЛА ЧЕРЕЗ ЗАПЯТУЮ, БОЛЬШЕ НИЧЕГО НЕ ПИШИ.')
    res_with_color_text = res_with_color.choices[0].message.content
    tuple_color = tuple(list(map(lambda x: int(x), res_with_color_text.split(','))))
    img = Image.new('RGB', (500, 500), tuple_color)
    # img.save(f'path/{tuple_color}.png', 'PNG')
    # final_img = FSInputFile(f'path/{tuple_color}.png', filename=f'{tuple_color}.jpg')
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    buffered.seek(0) 
    buffer_img = BufferedInputFile(buffered.getvalue(), 'color.jpeg')
    await message.answer_photo(photo=buffer_img, caption=f'Вот твой уникальный цвет в формате rgb: ({res_with_color_text})')
    await state.clear()
 
  finally:
    await loading_msg.delete()

  
@router.message(Req.message_to_recommend)
async def on_text_to_search_message(message: Message, state: FSMContext):
    loading_msg = ''
    try:
      await state.update_data(message_to_recommend=message.text)
      data = await state.get_data()
      art = data['art']
      filter_to_search = data['filter_to_search']
      loading_msg = await message.answer('Нейросеть отвечает на ваше сообщение...')
      res_with_bool_answer = await generate(f'Ответь одним словом "да", если {filter_to_search} {message.text} существует в области {art}, иначе ответь одним словом "нет"')
      if res_with_bool_answer.choices[0].message.content.lower().find('нет') != -1:
        await loading_msg.delete()
        await message.answer(f'Такого {filter_to_search} не существует, повтори попытку')
        return 
      await state.set_state(Res.message_with_response)
      choice_in_word = get_choice_in_art(art)
      res_with_recommendation = await generate(f'Посоветуй {choice_in_word} исходя из {filter_to_search}, который называется {message.text}. Если {message.text} - исполнитель или режиссёр, или писатель, то ни в коем случае не указывай произведения, созданные им. Не начинай сообщение ответ с утвердильных слов, типа "Конечно", "Хорошо" и тд')
      if not res_with_recommendation:
          await message.answer('Нейросеть не смогла дать ответ, повтори запрос позже')
      else:
          await message.answer(res_with_recommendation.choices[0].message.content)
          await state.update_data(message_with_ressponse=res_with_recommendation.choices[0].message.content)
      await state.clear()
    except:
      await message.answer('На сервере возникла ошибка, повторите ваш запрос позже')
      return
    finally:
      await loading_msg.delete()


#callback_query

@router.callback_query(F.data == 'Музыка', Req.art)
async def picks_music(callback: CallbackQuery, state: FSMContext):
    await state.update_data(art=callback.data)
    await state.set_state(Req.filter_to_search)
    await callback.answer('')
    await callback.message.edit_text('Выбери на основе чего ты хочешь найти рекомендацию', reply_markup=await kb.create_inline_keyboard(os.getenv('inline_with_music_fields').split(',')))

@router.callback_query(F.data == 'Книги', Req.art)
async def picks_books(callback: CallbackQuery, state: FSMContext):
    await state.update_data(art=callback.data)
    await state.set_state(Req.filter_to_search)
    await callback.answer('')
    await callback.message.edit_text('Выбери на основе чего ты хочешь найти рекомендацию', reply_markup=await kb.create_inline_keyboard(os.getenv('inline_with_book_fields').split(',')))

@router.callback_query(F.data == 'Фильмы', Req.art)
async def picks_films(callback: CallbackQuery, state: FSMContext):
    await state.update_data(art=callback.data)
    await state.set_state(Req.filter_to_search)
    await callback.answer('')
    await callback.message.edit_text('Выбери на основе чего ты хочешь найти рекомендацию', reply_markup=await kb.create_inline_keyboard(os.getenv('inline_with_film_fields').split(',')))

@router.callback_query(Req.filter_to_search)
async def message_to_recommend(callback: CallbackQuery, state: FSMContext):
    await callback.answer('')
    await state.update_data(filter_to_search=callback.data)
    await state.set_state(Req.message_to_recommend)
    data = await state.get_data()
    art = data['art']
    choice_in_filter = word_in_filter_choice[callback.data]
    choice_in_word = get_choice_in_art(art)
    choice_in_ending = get_choice_in_ending(art)
    await callback.message.edit_text(f'Введи {choice_in_filter}, чтобы найти произведения, подходящ{choice_in_ending} тебе по мнению нейросети')
