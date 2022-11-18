import requests
from bs4 import BeautifulSoup


class Authorization:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.session = requests.Session()

    def get_auth_data(self):
        url = "https://api.100points.ru/login"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"

        headers = {
            "user-agent": user_agent
        }

        data = {
            'email': self.login,
            'password': self.password
        }

        self.session.post(url, data=data, headers=headers)  # response

        cookies = [
            {
                'domain': key.domain,
                'name': key.name,
                'path': key.path,
                'value': key.value
            }
            for key in self.session.cookies
        ]

        return cookies, headers


def parse_vk(token) -> list:
    url = f"https://api.vk.com/method/board.getComments?access_token={token}&group_id=199470592&topic_id=49391401&v=5.131"
    response = requests.get(url).json()

    return [
        (target[0], target[1])
        for target in [item['text'].split('\n') for item in response['response']['items']]
    ]


def parse_100points(cookies_list: list, headers: dict, data_list: list) -> list:
    parse_data = []
    for module_vk, lesson_vk in data_list:
        session = requests.Session()
        session.headers = headers

        for cookies in cookies_list:
            session.cookies.set(**cookies)

        response = session.get(
            "https://api.100points.ru/student_homework/index?email=&name=&course_id=23&module_id=&lesson_id=&group_id=").text
        soup = BeautifulSoup(response, 'html.parser')
        module_list = [(module['value'], module.text.strip('\n').strip()) for module in
                       soup.find('select', id='module_id').find_all('option')]

        for module_value, module_name in module_list:
            if module_name == module_vk:
                selected_module_value = module_value
                break
        else:
            continue

        response = session.get(
            f"https://api.100points.ru/student_homework/index?email=&name=&course_id=23&module_id={selected_module_value}&lesson_id=&group_id=").text
        soup = BeautifulSoup(response, 'html.parser')
        lesson_list = [(lesson['value'], lesson.text.strip('\n').strip()) for lesson in
                       soup.find('select', id='lesson_id').find_all('option')]

        for lesson_value, lesson_name in lesson_list:
            if lesson_name == lesson_vk:
                selected_lesson_value = lesson_value
                break
        else:
            continue

        parse_url = f'https://api.100points.ru/exchange/index?email=&name=&course_id=&' \
                    f'module_id={selected_module_value}&lesson_id={selected_lesson_value}'
        response = session.get(parse_url).text
        soup = BeautifulSoup(response, 'html.parser')

        try:
            works_count = int(soup.find('div', id='example2_info').text.split()[-1])
        except Exception as ex:
            try:
                works_count = len(soup.find('tbody').find_all('tr'))
            except Exception as ex1:
                works_count = 0
                print(ex1)
            print(ex)

        parse_data.append(
            {
                'module_name': module_vk,
                'lesson_name': lesson_vk,
                'works_cnt': works_count
            }
        )

    return parse_data


def get_message_data(login, password, token):
    auth = Authorization(login, password)
    cookies_list, headers = auth.get_auth_data()
    data_list = parse_vk(token)
    parse_data = parse_100points(cookies_list, headers, data_list)
    return parse_data
