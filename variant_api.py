import requests
from dotenv import load_dotenv
import os
import json
import base64
from time import monotonic



def fetch_image(num):
    path_examples = os.listdir('examples')

    with open(f'examples/{path_examples[num]}', 'rb') as binary_file:
        base64_message = base64.b64encode(binary_file.read()).decode("utf-8")
        return base64_message

def create_task(api_key,num):
    url = 'https://api.anti-captcha.com/createTask'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = json.dumps({'clientKey': api_key,
            'task':
                {
                    'type': "ImageToTextTask",
                    'body': fetch_image(num),
                },
            })

    response = requests.post(url, headers=headers, data=data)
    task_id = response.json()['taskId']
    return task_id

def get_result(task_id,api_key):
    url = 'https://api.anti-captcha.com/getTaskResult'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }
    data = json.dumps({
        'clientKey': api_key,
        'taskId': task_id
    })
    response = requests.post(url,headers=headers,data=data)
    result = response.json()
    return result


def main():
    load_dotenv()
    api_key = os.getenv('CAPTCHA_KEY')


    path_examples = os.listdir('examples')
    amount = len(path_examples)
    tasks = []
    results = []
    start_time = monotonic()
    for num in range(amount):
        task_id = create_task(api_key,num)
        tasks.append(task_id)

    end_time = monotonic()
    result_time = end_time - start_time
    print(f'create tasks time:{result_time}')

    start_time = monotonic()
    for task in tasks:
        result = get_result(task, api_key)
        results.append(result)
    end_time = monotonic()
    result_time = end_time - start_time
    print(f'return result time:{result_time}')
    print(results)






if __name__=='__main__':
    main()

