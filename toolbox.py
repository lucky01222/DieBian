import os 
import pathlib
from gradio.themes.utils import ThemeAsset
import gradio as gr
import time
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")

from IPython.display import display, Code, Markdown
import copy
import glob
import shutil
import json
import io
import inspect
import requests
import re
import random
import string
import base64
import os.path
import sys

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseUpload
import email
from email import policy
from email.parser import BytesParser
from email.mime.text import MIMEText

os.environ['SSL_VERSION'] = 'TLSv1_2'

import warnings
warnings.filterwarnings("ignore")
from io import BytesIO





"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Part1
Gradio功能函数
    - bot:                       展示Chatbot结果函数，对应Chatbot的fn，逐字返回模型回答结果
    - add_text:                  加入用户对话信息函数，将用户的输入消息加入Chatbot中
    - add_file:                  加入用户文件信息函数，将用户的输入文件加入Chatbot中
    - create_theme_dropdown:     创建Gradio主题下拉列表函数，创建DropDown组建用于选择Theme
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""
def f1(function_1):
    
    print("function_1", function_1)
    
    return function_1


def predict(txt, chatbot, messages, model):
    chatbot.append((txt, None))
    yield from update_ui(chatbot=chatbot, msg="")
    
    messages.messages_append({'role': 'user', 'content': txt})
    messages = get_chat_response(chatbot=chatbot,
                                 model=model,
                                 messages=messages)
    
    return chatbot, messages
    



def bot(history):
    """
    展示Chatbot结果，对应Chatbot的fn，逐字返回模型回答结果
    
    :param history: 历史对话消息
    :return       : 加上本次模型回答的对话消息
    """
    response = "**That's cool!**"
    history[-1][1] = ""
    for character in response:
        history[-1][1] += character
        time.sleep(0.05)
        yield history

def add_user_text(history, text):
    """
    加入用户对话信息函数，将用户的输入消息加入Chatbot中
    
    :param history: Chatbot组件，记录历史对话消息
    :param text   : Textbox,记录当前用户输入的消息
    :return       : history, text
    """
    history = history + [(text, None)]
    return history, gr.Textbox(value="", interactive=False)

def print_system_text(history, text):
    """
    系统输出信息函数，将系统的输出消息加入Chatbot中并进行输出
    
    :param history: Chatbot组件，记录历史对话消息
    :param text   : Textbox,记录当前用户输入的消息
    :return       : history
    """
    history[-1][1] = ""
    for character in text:
        history[-1][1] += character
        time.sleep(0.05)
        yield history
    
    


def add_message(text, msg):
    """
    为ChatMessage类添加对话消息
    """
    msg.messages_append({'role': 'user', 'content': txt})
    return text, msg



def add_file(history, files):
    """
    加入用户文件信息函数，将用户的输入文件加入Chatbot中
    :param history: Chatbot组件，记录历史对话消息
    :param files  : Files组件，记录当前用户上传的文件
    :return       : Chatbot
    """
    for file in files:
        history = history + [((file.name,), None)]
    return history

def create_theme_dropdown():
    """
    创建Gradio主题下拉列表函数，创建Dropdown组件用于选择Theme
    :return       : Dropdown组件，更改主题的js代码
    """
    import gradio as gr

    asset_path = pathlib.Path().parent / "themes"
    themes = []
    for theme_asset in os.listdir(str(asset_path)):
        themes.append(
            (ThemeAsset(theme_asset), gr.Theme.load(str(asset_path / theme_asset)))
        )

    def make_else_if(theme_asset):
        return f"""
        else if (theme == '{str(theme_asset[0].filename)}') {{
            var theme_css = `{theme_asset[1]._get_theme_css()}`
        }}"""

    head, tail = themes[0], themes[1:]
    if_statement = f"""
        if (theme == "{str(head[0].filename)}") {{
            var theme_css = `{head[1]._get_theme_css()}`
        }} {" ".join(make_else_if(t) for t in tail)}
    """

    latest_to_oldest = sorted([t[0] for t in themes], key=lambda asset: asset.filename)[
        ::-1
    ]
    latest_to_oldest = [str(t.filename) for t in latest_to_oldest]

    component = gr.Dropdown(
        choices=latest_to_oldest,
        value=latest_to_oldest[0],
        render=False,
        label="Select Version",
        container=False
    )

    return (
        component,
        f"""
        (theme) => {{
            if (!document.querySelector('.theme-css')) {{
                var theme_elem = document.createElement('style');
                theme_elem.classList.add('theme-css');
                document.head.appendChild(theme_elem);
            }} else {{
                var theme_elem = document.querySelector('.theme-css');
            }}
            {if_statement}
            theme_elem.innerHTML = theme_css;
        }}
    """,
    )



"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Part2
InterProject类辅助函数:
    - create_or_get_folder:        创建或获取文件夹ID，本地存储时获取文件夹路径
    - create_or_get_doc:           创建或获取文件ID，本地存储时获取文件路径
    - get_file_content:            获取文档的具体内容，需要区分是读取谷歌云文档还是读取本地文档
    - append_content_in_doc:       创建文档，或为指定的文档增加内容，需要区分是否是云文档
    - clear_content_in_doc:        清空指定文档的全部内容，需要区分是否是云文档
    - list_files_in_folder:        列举当前文件夹的全部文件，需要区分是读取谷歌云盘文件夹还是本地文件夹
    - rename_doc_in_drive:         修改指定的文档名称，需要区分是云文件还是本地文件
    - delete_all_files_in_folder:  删除某文件夹内全部文件，需要区分谷歌云文件夹还是本地文件夹
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""
def create_or_get_folder(folder_name, upload_to_google_drive=False):
    """
    创建或获取文件夹ID，本地存储时获取文件夹路径
    """
    if upload_to_google_drive:
        # 若存储至谷歌云盘，则获取文件夹ID
        creds = Credentials.from_authorized_user_file('token.json')
        drive_service = build('drive', 'v3', credentials=creds)

        # 查询是否已经存在该名称的文件夹
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = drive_service.files().list(q=query).execute()
        items = results.get('files', [])

        # 如果文件夹不存在，则创建它
        if not items:
            folder_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = drive_service.files().create(body=folder_metadata).execute()
            folder_id = folder['id']
        else:
            folder_id = items[0]['id']
        
    else:
        # 若存储本地，则获取文件夹路径，且同时命名为folder_id
        folder_path = os.path.join('./', folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        folder_id = folder_path
        
    return folder_id

def create_or_get_doc(folder_id, doc_name, upload_to_google_drive=False):
    """
    创建或获取文件ID，本地存储时获取文件路径
    """    
    if upload_to_google_drive:
        creds = Credentials.from_authorized_user_file('token.json')
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # 查询文件夹中是否已经存在该名称的文档
        query = f"name='{doc_name}' and '{folder_id}' in parents"
        results = drive_service.files().list(q=query).execute()
        items = results.get('files', [])

        # 如果文档不存在，创建它
        if not items:
            doc_metadata = {
                'name': doc_name,
                'mimeType': 'application/vnd.google-apps.document',
                'parents': [folder_id]
            }
            doc = drive_service.files().create(body=doc_metadata).execute()
            document_id = doc['id']
        else:
            document_id = items[0]['id']
            
    # 若存储本地，则获取文件夹路径，且同时命名为document_id
    else: 
        file_path = os.path.join(folder_id, f'{doc_name}.md')
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write('')  # 创建一个带有标题的空Markdown文件
        document_id = file_path
        
    return document_id

def get_file_content(file_id, upload_to_google_drive=False):
    """
    获取文档的具体内容，需要区分是读取谷歌云文档还是读取本地文档
    """
    # 读取谷歌云文档
    if upload_to_google_drive:
        creds = Credentials.from_authorized_user_file('token.json')
        service = build('drive', 'v3', credentials=creds)
        os.environ['SSL_VERSION'] = 'TLSv1_2'
        request = service.files().export_media(fileId=file_id, mimeType='text/plain')
        content = request.execute()
        decoded_content = content.decode('utf-8')
        
    # 读取本地文档
    else:
        with open(file_id, 'r', encoding='utf-8') as file:
            decoded_content = file.read()
    return decoded_content

def append_content_in_doc(folder_id, doc_id, dict_list, upload_to_google_drive=False):
    """
    创建文档，或为指定的文档增加内容，需要区分是否是云文档
    """
    # 将字典列表转换为JSON字符串
    json_string = json.dumps([dict_.json() if isinstance(dict_, openai.types.chat.chat_completion_message.ChatCompletionMessage) else dict_ for dict_ in dict_list], indent=4, ensure_ascii=False)

    # 若是谷歌云文档
    if upload_to_google_drive:
        creds = Credentials.from_authorized_user_file('token.json')
        drive_service = build('drive', 'v3', credentials=creds)
        docs_service = build('docs', 'v1', credentials=creds)

        # 获取文档的当前长度
        document = docs_service.documents().get(documentId=doc_id).execute()
        end_of_doc = document['body']['content'][-1]['endIndex'] - 1  

        # 追加Q-A内容到文档
        requests = [{
            'insertText': {
                'location': {'index': end_of_doc},
                'text': json_string + '\n\n'   # 追加JSON字符串和两个换行，使格式整洁
            }
        }]
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        
    # 若是本地文档
    else:
        with open(doc_id, 'a', encoding='utf-8') as file:
            file.write(json_string)  # 追加JSON字符串

def clear_content_in_doc(doc_id, upload_to_google_drive=False):
    """
    清空指定文档的全部内容，需要区分是否是云文档
    """
    # 如果是清除谷歌云文档内容
    if upload_to_google_drive:
        creds = Credentials.from_authorized_user_file('token.json')
        docs_service = build('docs', 'v1', credentials=creds)

        # 获取文档的当前长度
        document = docs_service.documents().get(documentId=doc_id).execute()
        end_of_doc = document['body']['content'][-1]['endIndex'] - 1

        # 创建删除内容的请求
        requests = [{
            'deleteContentRange': {
                'range': {
                    'startIndex': 1,  # 文档的开始位置
                    'endIndex': end_of_doc  # 文档的结束位置
                }
            }
        }]

        # 执行删除内容的请求
        docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
        
    # 如果是清除本地文档内容
    else:
        with open(doc_id, 'w') as file:
            pass  # 清空文件内容

def list_files_in_folder(folder_id, upload_to_google_drive=False):
    """
    列举当前文件夹的全部文件，需要区分是读取谷歌云盘文件夹还是本地文件夹
    """
    # 读取谷歌云盘文件夹内文件
    if upload_to_google_drive:
        creds = Credentials.from_authorized_user_file('token.json')
        drive_service = build('drive', 'v3', credentials=creds)

        # 列出文件夹中的所有文件
        query = f"'{folder_id}' in parents"
        results = drive_service.files().list(q=query).execute()
        files = results.get('files', [])

        # 获取并返回文件名称列表
        file_names = [file['name'] for file in files]
        
    # 读取本地文件夹内文件
    else:
        file_names = [f for f in os.listdir(folder_id) if os.path.isfile(os.path.join(folder_id, f))]
    return file_names

def rename_doc_in_drive(folder_id, doc_id, new_name, upload_to_google_drive=False):
    """
    修改指定的文档名称，需要区分是云文件还是本地文件
    """
    # 若修改云文档名称
    if upload_to_google_drive:
        creds = Credentials.from_authorized_user_file('token.json')
        drive_service = build('drive', 'v3', credentials=creds)

        # 创建更新请求以更改文档名称
        update_request_body = {
            'name': new_name
        }

        # 发送更新请求
        update_response = drive_service.files().update(
            fileId=doc_id,
            body=update_request_body,
            fields='id,name'
        ).execute()

        # 返回更新后的文档信息，包括ID和新名称
        update_name = update_response['name']
        
    # 若修改本地文档名称
    else:
        # 分解原始路径以获取目录和扩展名
        directory, old_file_name = os.path.split(doc_id)
        extension = os.path.splitext(old_file_name)[1]

        # 用新名称和原始扩展名组合新路径
        new_file_name = new_name + extension
        new_file_path = os.path.join(directory, new_file_name)

        # 重命名文件
        os.rename(doc_id, new_file_path)
        
        update_name=new_name
    
    return update_name

def delete_all_files_in_folder(folder_id, upload_to_google_drive=False):
    """
    删除某文件夹内全部文件，需要区分谷歌云文件夹还是本地文件夹
    """
    # 如果是谷歌云文件夹
    if upload_to_google_drive:
        creds = Credentials.from_authorized_user_file('token.json')
        drive_service = build('drive', 'v3', credentials=creds)

        # 列出文件夹中的所有文件
        query = f"'{folder_id}' in parents"
        results = drive_service.files().list(q=query).execute()
        files = results.get('files', [])

        # 遍历并删除每个文件
        for file in files:
            file_id = file['id']
            drive_service.files().delete(fileId=file_id).execute()
            # print(f"Deleted file: {file['name']} (ID: {file_id})")
       
    # 如果是本地文件夹
    else:
        for filename in os.listdir(folder_id):
            file_path = os.path.join(folder_id, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')



















"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Part4
其他小工具:
    - update_ui:         刷新用户界面
    - find_free_port:    返回当前系统中可用的未使用端口
    - auto_functions:    Chat模型的functions参数编写函数
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""

def update_ui(txt, chatbot, md_dropdown, messages):  # 刷新界面
    """
    刷新用户界面
    """

    yield txt, chatbot, md_dropdown, messages


def find_free_port():
    """
    返回当前系统中可用的未使用端口。
    """
    import socket
    from contextlib import closing

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]

def auto_functions(functions_list):
    """
    Chat模型的functions参数编写函数
    :param functions_list: 包含一个或者多个函数对象的列表；
    :return：满足Chat模型functions参数要求的functions对象
    """
    def functions_generate(functions_list):
        # 创建空列表，用于保存每个函数的描述字典
        functions = []
        
        def chen_ming_algorithm(data):
            """
            陈明算法函数，该函数定义了一种特殊的数据集计算过程
            :param data: 必要参数，表示带入计算的数据表，用字符串进行表示
            :return：陈明函数计算后的结果，返回结果为表示为JSON格式的Dataframe类型对象
            """
            df_new = pd.read_json(data)
            res = np.sum(df_new, axis=1) - 1
            return res.to_json(orient='records')
        
        chen_ming_function_description = inspect.getdoc(chen_ming_algorithm)
        
        chen_ming_function_name = chen_ming_algorithm.__name__
        
        chen_ming_function = {"name": "chen_ming_algorithm",
                              "description": "用于执行陈明算法的函数，定义了一种特殊的数据集计算过程",
                              "parameters": {"type": "object",
                                             "properties": {"data": {"type": "string",
                                                                     "description": "执行陈明算法的数据集"},
                                                           },
                                             "required": ["data"],
                                            },
                             }

        
        # 对每个外部函数进行循环
        for function in functions_list:
            # 读取函数对象的函数说明
            function_description = inspect.getdoc(function)
            # 读取函数的函数名字符串
            function_name = function.__name__

            user_message1 = '以下是某的函数说明：%s。' % chen_ming_function_description +\
                            '根据这个函数的函数说明，请帮我创建一个function对象，用于描述这个函数的基本情况。这个function对象是一个JSON格式的字典，\
                            这个字典有如下5点要求：\
                            1.字典总共有三个键值对；\
                            2.第一个键值对的Key是字符串name，value是该函数的名字：%s，也是字符串；\
                            3.第二个键值对的Key是字符串description，value是该函数的函数的功能说明，也是字符串；\
                            4.第三个键值对的Key是字符串parameters，value是一个JSON Schema对象，用于说明该函数的参数输入规范。\
                            5.输出结果必须是一个JSON格式的字典，只输出这个字典即可，前后不需要任何前后修饰或说明的语句' % chen_ming_function_name
            
            
            assistant_message1 = json.dumps(chen_ming_function)
            
            user_prompt = '现在有另一个函数，函数名为：%s；函数说明为：%s；\
                          请帮我仿造类似的格式为当前函数创建一个function对象。' % (function_name, function_description)
            
            client = openai.OpenAI()
            response = client.chat.completions.create(
                              model="gpt-4-1106-preview",
                              messages=[
                                {"role": "user", "name":"example_user", "content": user_message1},
                                {"role": "assistant", "name":"example_assistant", "content": assistant_message1},
                                {"role": "user", "name":"example_user", "content": user_prompt}]
                            )
            functions.append(json.loads(response.choices[0].message.content))
        return functions
    
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        try:
            functions = functions_generate(functions_list)
            break  # 如果代码成功执行，跳出循环
        except Exception as e:
            attempts += 1  # 增加尝试次数
            print("发生错误：", e)
            print("由于模型limit rate导致报错，即将暂停1分钟，1分钟后重新尝试调用模型")
            time.sleep(60)
            
            if attempts == max_attempts:
                print("已达到最大尝试次数，程序终止。")
                raise  # 重新引发最后一个异常
            else:
                print("正在重新运行...")
    return functions