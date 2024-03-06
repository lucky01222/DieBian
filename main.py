import os; os.environ['no_proxy'] = '*' # 避免代理网络产生意外污染


def main():
    import gradio as gr
    if gr.__version__ not in ['4.19.2']:
        raise ModuleNotFoundError("您的gradio包版本与所需不符，请运行 `pip install -r requirements.txt` 指令安装Gradio, 详情信息见requirements.txt.")
    # 导入设置
    from config import LLM_MODEL, AVAIL_LLM_MODELS, INIT_SYS_PROMPT, THEME, ADD_WAIFU, help_menu_description, PATH_PRIVATE_UPLOAD, CONCURRENT_COUNT, OPEN_AI_API_KEY, VERSION, WEB_PORT
    # 导入工具箱
    from toolbox import bot, add_user_text, print_system_text, add_message, add_file, create_theme_dropdown, find_free_port, predict, f1
    
    from llm_predict import add_task_decomposition_prompt_fn, modify_prompt_fn, get_gpt_response, get_chat_response, is_code_response_valid, check_get_final_function_response
    # 导入各类
    from ChatMessages import ChatMessages
    from AvailableFunctions import AvailableFunctions
    from InterProject import InterProject
    # 导入外部函数及其描述信息
    from functions import python_inter, upload_image_to_drive, fig_inter
    from functions_info import python_inter_function_info, fig_inter_function_info

    messages = ChatMessages(system_content_list=[], question="你好")
    
    
    # 如果WEB_PORT是-1, 则随机选取WEB端口
    PORT = find_free_port() if WEB_PORT <= 0 else WEB_PORT
    # 标题HTML
    title_html = f"""<h1 align=\"center\">蝶变·智习室学术工具 {VERSION}</h1>"""
    
    # 是否添加live2d模型
    if ADD_WAIFU:
        head = f"""<script src="https://fastly.jsdelivr.net/gh/stevenjoezhang/live2d-widget@latest/autoload.js"></script>"""
    else:
        head = None
    
    # 构建gradio demo

    theme_dropdown, theme_js = create_theme_dropdown()  # 主题菜单及其js代码
    with gr.Blocks(title="蝶变·智习室学术工具", 
                   head=head, 
                   theme=gr.themes.Base.load(path='themes/{}.json'.format(THEME))) as demo:  # 加载模型和主题
        gr.HTML(title_html)  # 加载HTML标题
        # 菜单栏，暂设三个菜单：文件上传，更换模型，界面外观
        with gr.Row():
            with gr.Accordion("设置", open=False, elem_id="config-panel"):
                with gr.Tab("上传文件", elem_id="interact-panel"):
                    gr.Markdown("请上传本地文件/压缩包供“函数插件区”功能调用。请注意: 上传文件后会自动把输入区修改为相应路径")
                    file_upload = gr.Files(label="任何文件，推荐上传压缩文件(zip,tar)", file_count="multiple", elem_id="elem_upload_float")
                    
                with gr.Tab("更换模型", elem_id='interact-panel'):
                    md_dropdown = gr.Dropdown(AVAIL_LLM_MODELS, value=LLM_MODEL, label="更换LLM模型/请求源", container=False)
                    modify_prompt = gr.Checkbox(label="提示词修改",elem_id="elem_function_1")
                    add_task_decomposition = gr.Checkbox(label="复杂任务拆解",elem_id="elem_function_1")
                    
                with gr.Tab("界面外观", elem_id="interact-panel"):
                    theme_dropdown.render()
                    dark_mode_btn = gr.Button("切换界面明暗 ☀", variant="secondary",size='sm')
                    dark_mode_btn.click(None, None, None, js="""
            () => {
                document.body.classList.toggle('dark');
            }
            """)
                with gr.Tab("关于我们", elem_id="interact-panel"):
                    gr.Markdown(help_menu_description)  # 
        gr_L1 = lambda: gr.Row()
        gr_L2 = lambda scale, elem_id: gr.Column(scale=scale, elem_id=elem_id, min_width=550)

        with gr_L2(scale=3, elem_id='gpt-chat'):
            chatbot = gr.Chatbot(label=f"当前模型:{LLM_MODEL}", 
                                 elem_id="gpt-chatbot", 
                                 avatar_images=((os.path.join("pictures/avatar_png/human_1.png")),
                                                (os.path.join("pictures/avatar_png/robot_1.png"))),height=500)
    
        with gr_L2(scale=1, elem_id="gpt-panel"):
            with gr.Accordion("输入区", open=True, elem_id="input-panel") as area_input_primary:
                with gr.Row():
                    txt = gr.Textbox(show_label=False, placeholder='请在这里输入你的问题', elem_id='user-input')
                with gr.Row():
                    submitBtn = gr.Button("提交", elem_id="elem_submit", variant="primary")
                with gr.Row():
                    resetBtn = gr.Button("重置", size='sm',elem_id="elem_reset", variant="secondary")
                    # 清除按钮
                    clearBtn = gr.ClearButton(txt, value="清除", size='sm',  elem_id="elem_clear", variant="secondary")
                with gr.Row():
                    status = gr.Markdown(f"Tip: 按Enter提交, 按Shift+Enter换行。当前模型: {LLM_MODEL}", elem_id='state-panel')
    
        # 主题更改
        theme_dropdown.select(None, theme_dropdown, None, js=theme_js)
        messages = gr.State(messages)
       
        # 提交问题
        txt_msg = txt.submit(get_chat_response, [txt, chatbot, md_dropdown, messages, modify_prompt, add_task_decomposition], [txt, chatbot, md_dropdown, messages]).then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)
        
        txt_msg = submitBtn.click(get_chat_response, [txt, chatbot, md_dropdown, messages, modify_prompt, add_task_decomposition], [txt, chatbot, md_dropdown, messages]).then(lambda: gr.Textbox(interactive=True), None, [txt], queue=False)
    
        # 文件上传
        file_msg = file_upload.upload(add_file, [chatbot, file_upload], [chatbot], queue=False).then(bot, chatbot, chatbot)
    
        # 重置按钮
        resetBtn.click(lambda: (None, [], 已重置), None, [txt, chatbot, status])    

    def run_delayed_tasks():
        import threading, webbrowser, time
        print(f"如果浏览器没有自动打开，请复制并转到以下URL：")
        print(f"\t「亮色主题已启用（支持动态切换主题）」: http://localhost:{PORT}")

        def open_browser(): time.sleep(2); webbrowser.open_new_tab(f"http://localhost:{PORT}")
        threading.Thread(target=open_browser, name="open-browser", daemon=True).start() # 打开浏览器页面

    run_delayed_tasks()
    
    demo.launch(
        share=True,
        server_name="0.0.0.0",
        server_port=PORT,
        max_threads=CONCURRENT_COUNT,
        blocked_paths=["config.py"])


if __name__ == "__main__":
    main()
