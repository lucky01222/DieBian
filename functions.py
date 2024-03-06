import os.path
import matplotlib
import inspect

from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseUpload

from io import BytesIO

"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
Functions.py
大模型能够调用的外部函数库
    - python_inter:              该函数专门用于执行非绘图类python代码，并获取最终查询或处理结果。
    - upload_image_to_drive:     将指定的fig对象上传至谷歌云盘，供fig_inter调用
    - add_file:                  加入用户文件信息函数，将用户的输入文件加入Chatbot中
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""

def python_inter(py_code, g='globals()'):
    """
    该函数专门用于执行非绘图类python代码，并获取最终查询或处理结果。若是设计绘图操作的Python代码，则需要调用fig_inter函数来执行。
    :param py_code: 字符串形式的Python代码，用于执行对telco_db数据库中各张数据表进行操作
    :param g: g，字符串形式变量，表示环境变量，无需设置，保持默认参数即可
    :return：代码运行的最终结果
    """    
    
    global_vars_before = set(g.keys())
    try:
        exec(py_code, g)            
    except Exception as e:
        return f"代码执行时报错{e}"
    global_vars_after = set(g.keys())
    new_vars = global_vars_after - global_vars_before
    # 若存在新变量
    if new_vars:
        result = {var: g[var] for var in new_vars}
        return str(result)
    # 若不存在新变量，即有可能是代码是表达式，也有可能代码对相同变量重复赋值
    else:
        try:
            # 尝试如果是表达式，则返回表达式运行结果
            return str(eval(py_code, g))
        # 若报错，则先测试是否是对相同变量重复赋值
        except Exception as e:
            try:
                exec(py_code, g)
                return "已经顺利执行代码"
            except Exception as e:
                pass
            # 若不是重复赋值，则报错
            return f"代码执行时报错{e}"


def upload_image_to_drive(figure, folder_id = '1Ju8-ZHuEfyCRlPCFiqwuypn7B0A2s6zF'):
    """
    将指定的fig对象上传至谷歌云盘
    """
    folder_id = folder_id        # 此处需要改为自己的谷歌云盘文件夹ID
    creds = Credentials.from_authorized_user_file('token.json')
    drive_service = build('drive', 'v3', credentials=creds)
    
    # 1. Save image to Google Drive
    buf = BytesIO()
    figure.savefig(buf, format='png')
    buf.seek(0)
    media = MediaIoBaseUpload(buf, mimetype='image/png', resumable=True)
    file_metadata = {
        'name': 'YourImageName.png',
        'parents': [folder_id],
        'mimeType': 'image/png'
    }
    image_file = drive_service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id,webContentLink'  # Specify the fields to be returned
    ).execute()
    
    return image_file["webContentLink"]


def fig_inter(py_code, g='globals()'):
    """
    用于执行一段包含可视化绘图的Python代码，并最终获取一个图片类型对象
    :param py_code: 字符串形式的Python代码，用于根据需求进行绘图，代码中必须包含Figure对象创建过程
    :return：代码运行的最终结果
    """    
    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns
    # 若存在plt.show()，则删除
    py_code = 'import matplotlib.pyplot as plt\n' + py_code.replace('plt.show()', '') + '\nfig = plt.gcf()\nplt.close()'+ '\nplt.rcParams.update(plt.rcParamsDefault)'
    
    # 创建一个命名空间字典来存储可能被代码修改的全局变量
    g = {}

    try:
        exec(py_code, g)            
    except Exception as e:
        return f"代码执行时报错{e}"
    fig = g["fig"]
    
    # 上传图片
    try:
        fig_url = upload_image_to_drive(fig)
        res = f"已经成功运行代码，并已将代码创建的图片存储至：{fig_url}"
        
    except Exception as e:
        res = "无法上传图片至谷歌云盘，请检查谷歌云盘文件夹ID，并检查当前网络情况"
        
    print(res)
    return res