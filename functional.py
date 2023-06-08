import csv
import time
import logging

from typing import List
from pyrogram import Client


api_id = 0
api_hash = ""


def parse_cvs(filepath: str) -> List[str]:
    with open(filepath, newline='') as csvfile:
        urls_reader = csv.reader(csvfile, delimiter='\n')
        urls = []
        for url in urls_reader:
            urls.append(url[0])
        return urls


async def join_chats():
    filepath = '.\\urls.csv'
    app = Client('account', api_id=api_id, api_hash=api_hash)
    urls = parse_cvs(filepath)
    i = 0

    logging.info('Начинаю вступать в группы')

    for url in urls:
        i += 1
        await app.join_chat(url)
        if i == 5:
            logging.info('Вступил в 5 групп, ожидаю 5 минут, чтобы продолжить')
            time.sleep(301)
