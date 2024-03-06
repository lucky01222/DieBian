import os

# 当前采用的大模型
LLM_MODEL= 'gpt-3.5-turbo-0125'
# 可以载入的大模型
AVAIL_LLM_MODELS = ["gpt-4-1106-preview", 
                    "gpt-4-0125-preview", 
                    "gpt-4-1106-vision-preview",
                    "gpt-3.5-turbo-0125",]

# 系统提示
INIT_SYS_PROMPT = "你是以为致力于助力科研工作者进行科学研究的助手"

# 当前主题
THEME = "miku@1.2.2"

# 可选主题，如需添加新主题，无需修改此列表，直接将json文件放入themes文件中即可，能够自动检测
# gradio主题网址：https://huggingface.co/spaces/gradio/theme-gallery
AVAIL_THEMES = ["Anime@0.0.1", 
                "dracula_revamped@0.3.9",
                "HaleyCH_Theme@0.0.1", 
                "miku@1.2.2", 
                "pakustan@0.0.1",
                "storj_theme@0.0.1",
                "xkcd@0.0.4"
]

# 是否添加Live2d模型
ADD_WAIFU = True

# 关于我们
help_menu_description="关于我们"


# 临时的上传文件夹位置，请勿修改
PATH_PRIVATE_UPLOAD = "private_upload"

# 版本
VERSION = 1.0

# 设置gradio的并行线程数（不需要修改）
CONCURRENT_COUNT = 100

# 网页开启的端口,-1表示随机选择可用端口
WEB_PORT = -1 

# API_KEY
# 在这里放入您的大模型API_KEY，请注意不要将该信息透露给其他人，否则可能造成额外费用。

# GPT模型
OPEN_AI_API_KEY = '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'

