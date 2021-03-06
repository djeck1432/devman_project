import os
import json
import base64
import asks
from dotenv import load_dotenv
from async_timeout import timeout
from anyio import create_task_group,run
import asyncio
from time import monotonic


async def create_task_id(api_key, base64_image):
    url = 'https://api.anti-captcha.com/createTask'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = json.dumps({'clientKey': api_key,
                       'task':
                           {
                               'type': "ImageToTextTask",
                               'body': base64_image,
                           },
                       })
    response = await asks.request('POST',url,headers=headers,data=data)
    response.raise_for_status()
    task_id = response.json()['taskId']
    return task_id

async def get_captcha_text(api_key, task_id):
    url = 'https://api.anti-captcha.com/getTaskResult'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = json.dumps({
        'clientKey': api_key,
        'taskId': task_id
    })
    response = await asks.request('POST',url, headers=headers, data=data)
    response.raise_for_status()
    result = response.json()
    captcha_solution = result.get('solution')
    if captcha_solution:
        captcha_text = captcha_solution['text']
        return captcha_text


async def solve_captcha(api_key,base64_image,max_time=20,response_timeout=10):#FIXME
    #TODO Отправлять каждую секудну запрос до получения позитивного ответа
    try:
        async with timeout(max_time) as cm:
            start_time = monotonic()
            task_id = await create_task_id(api_key, base64_image)
            end_time = monotonic()
            print(f'Create task id: {end_time-start_time}')
            #description, why here is sleep(5-10sec) read in the doc https://anticaptcha.atlassian.net/wiki/spaces/API/pages/196633
            await asyncio.sleep(response_timeout)

            start_time = monotonic()
            result_text = await get_captcha_text(api_key, task_id)
            while True:
                if result_text is not None:
                    break
                await asyncio.sleep(1)
                print('repeat result text 1 ')
                result_text = await get_captcha_text(api_key, task_id)

            end_time = monotonic()
            print(f'Get result: {end_time-start_time}')
            print(result_text)
    except asyncio.TimeoutError:
        print('finish procces')





#debugin function
def fetch_image(path_example):

    with open(f'new_examples/{path_example}', 'rb') as binary_file:
        base64_message = base64.b64encode(binary_file.read()).decode("utf-8")
        return base64_message


#debugin  function
async def main():
    load_dotenv()
    api_key = os.getenv('CAPTCHA_KEY')
    path_examples = os.listdir('new_examples')


    async with create_task_group() as captcha:
        for path_example in path_examples:
            base64_message = fetch_image(path_example)
            await captcha.spawn(solve_captcha,api_key,base64_message)


if __name__=='__main__':
    run(main)