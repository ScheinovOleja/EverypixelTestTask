import asyncio
import os
from asyncio import sleep

from datetime import date
from PIL import Image, ImageDraw, ImageFont
from codetiming import Timer


async def resize(work_queue):
    """
    Функция изменения размера изображения с сохранением пропорций.
    :param work_queue:
    :return:
    """
    global path_out, scale
    try:
        img = await work_queue.get()
        with Image.open(img) as old_image:
            name = img.split('/')[-1].split('.')[0] + '_resized.' + old_image.format.lower()
            new_width = int(old_image.size[0] * scale)
            new_height = int(old_image.size[1] * scale)
            new_image = old_image.resize((new_width, new_height))
            new_image.save(os.path.join(os.getcwd(), path_out, name), old_image.format)
        # Чтобы не удалялись исходные изображения. Я мог сделать сохранение в той же директории и потом перенос
        # изображения в новую директорию, но я считаю, что это больше нагружает скрипт, чем создание и удаление
        # os.remove(os.path.join(os.getcwd(), path_in, img.split('/')[-1]))
    except IOError as err:
        print(err)


async def paste_date(work_queue):
    """
    Функция вставки даты на изображение.
    :param work_queue:
    :return:
    """
    global path_out, scale
    try:
        img = await work_queue.get()
        with Image.open(img) as old_image:
            text_image = ImageDraw.Draw(old_image)
            font = ImageFont.truetype("fonts/arial.ttf", 24)
            name = img.split('/')[-1].split('.')[0] + '_date.' + old_image.format.lower()
            text_image.text((old_image.size[0] - 150, old_image.size[1] - 20), f'{date.today()}', fill='#ff2400',
                            font=font)
            old_image.save(os.path.join(os.getcwd(), path_out, name), old_image.format)
        # os.remove(os.path.join(os.getcwd(), path_in, img.split('/')[-1]))
    except IOError as err:
        print(err)


async def paste_watermark(work_queue):
    """
    Функция вставления вотермарки на изображение в нулевые координаты
    :param work_queue:
    :return:
    """
    global path_out, scale
    try:
        img = await work_queue.get()
        transparent = 65
        with Image.open(img) as old_image:
            name = img.split('/')[-1].split('.')[0] + '_watermarked.' + old_image.format.lower()
            with Image.open('copyright.png') as watermark:
                # Создание прозрачности было найдено на просторах гугла
                if watermark.mode != 'RGBA':
                    alpha = Image.new('L', watermark.size, 255)
                    watermark.putalpha(alpha)
                paste_mask = watermark.split()[3].point(lambda i: i * transparent / 100)
                old_image.paste(watermark, (0, 0), mask=paste_mask)
            old_image.save(os.path.join(os.getcwd(), path_out, name), old_image.format)
        # os.remove(os.path.join(os.getcwd(), path_in, img.split('/')[-1]))
    except IOError as err:
        print(err)


async def check_img(path_input, option):
    # Создание очереди выполнения
    work_queue = asyncio.Queue()
    # Помещение "задач" в очередь
    i = 0
    for img in os.listdir(path_input):
        i += 1
        await work_queue.put(os.path.join(os.getcwd(), path_input, img))
    if i == 0:
        return
    # Запуск задач. Timer использую только для отслеживания времени выполнения. Удобно же)
    with Timer(text="\n\nОбщее затраченное время: {:.10f}"):
        # Запуск задач
        tasks = []
        for _ in range(i):
            if option == 'resize':
                task = asyncio.create_task(resize(work_queue))
            elif option == 'date':
                task = asyncio.create_task(paste_date(work_queue))
            elif option == 'watermark':
                task = asyncio.create_task(paste_watermark(work_queue))
            else:
                break
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)
    print(f'Количество файлов - {i}')
    await sleep(1)


if __name__ == '__main__':
    path_in = 'input_img'
    path_out = 'output_img'
    # Множитель увеличения изображения
    scale = 1.5

    # Опция для основной задачи
    # option = 'resize'
    option = 'date'
    # option = 'watermark'
    while True:
        asyncio.run(check_img(path_input=path_in, option=option))
