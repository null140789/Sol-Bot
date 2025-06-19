import time
import requests
from telegram import Bot

# === Конфигурация ===
BOT_TOKEN = '7767116702:AAFgIeT6W9GpONbHdVpwvreFHx5LVNd-TtQ'
CHAT_ID = '6811658155'
LIQUIDITY_THRESHOLD = 1000  # В USD

bot = Bot(token=BOT_TOKEN)

def get_new_tokens():
    url = 'https://api.dexscreener.com/latest/dex/search?q=solana'
    response = requests.get(url)

    print("Статус код:", response.status_code)
    print("Ответ сервера:", response.text[:300])  # Показываем часть ответа для отладки

    try:
        data = response.json()
    except Exception as e:
        print("Ошибка при парсинге JSON:", e)
        return []

    tokens = data.get('pairs', [])
    new_tokens = []

    for token in tokens:
        if token.get('chainId') != 'solana':
            continue
        liquidity = token.get('liquidity', {}).get('usd', 0)
        if liquidity and liquidity >= LIQUIDITY_THRESHOLD:
            new_tokens.append({
                'name': token.get('baseToken', {}).get('name'),
                'symbol': token.get('baseToken', {}).get('symbol'),
                'liquidity': liquidity,
                'url': token.get('url')
            })
    return new_tokens

def send_signals(tokens):
    for token in tokens:
        message = (
            f"💥 Новая монета на Solana!\n\n"
            f"🪙 Название: {token['name']}\n"
            f"🔤 Символ: {token['symbol']}\n"
            f"💧 Ликвидность: ${token['liquidity']:.2f}\n"
            f"🔗 Ссылка: {token['url']}"
        )
        bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    sent = set()
    while True:
        try:
            tokens = get_new_tokens()
            for token in tokens:
                key = token['symbol'] + str(token['liquidity'])
                if key not in sent:
                    send_signals([token])
                    sent.add(key)
            time.sleep(300)  # Проверка каждые 5 минут
        except Exception as e:
            print("Ошибка в main():", e)
            time.sleep(60)

if __name__ == '__main__':
    main()
