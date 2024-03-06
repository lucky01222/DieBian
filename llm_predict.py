from toolbox import update_ui
import gradio as gr
import openai
"""
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
GPT模型调用函数:
    - add_task_decomposition_prompt:    当开启增强模式时，任何问题首次尝试作答时都会调用本函数，创建一个包含任务拆解新message
    - modify_prompt_fn:                    当开启开发者模式时，会让用户选择是否添加COT提示模板或其他提示模板，创建修改好的新message
    - get_gpt_response:                 负责调用Chat模型并获得模型回答函数
    - get_chat_response:                负责完整执行一次对话的最高层函数
    - is_code_response_valid:           负责完整执行一次外部函数调用的最高层函数
    - check_get_final_function_response:负责执行外部函数运行结果审查工作
    - is_text_response_valid:           负责执行文本内容创建审查工作
    
    
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
"""

def add_task_decomposition_prompt_fn(messages):
    """
    当开启增强模式时，任何问题首次尝试作答时都会调用本函数，创建一个包含任务拆解Few-shot的新的message.
    :param md_dropdown: 必要参数，表示调用的大模型名称
    :param available_functions:可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况。\
    默认值为None，表示不存在外部函数。
    :return : task_decomp_few_shot,一个包含任务拆解Few-shot提示事例的massage
    """
    # 任务拆解Few-shot
    # 第一个提示实例
    user_question1 = '请问谷歌云邮箱是什么？'
    user_message1_content = "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。" % user_question1
    assistant_message1_content = '谷歌云邮箱是指Google Workspace（原G Suite）中的Gmail服务，\
    它是一个安全、智能、易用的电子邮箱，有15GB的免费存储空间，可以直接在电子邮件中接收和存储邮件。\
    Gmail 邮箱会自动过滤垃圾邮件和病毒邮件，并且可以通过电脑或手机等移动设备在任何地方查阅邮件。\
    您可以使用搜索和标签功能来组织邮件，使邮件处理更为高效。'

    # 第二个提示示例
    user_question2 = '请帮我介绍下OpenAI。'
    user_message2_content = "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。" % user_question2
    assistant_message2_content = 'OpenAI是一家开发和应用友好人工智能的公司，\
    它的目标是确保人工通用智能（AGI）对所有人都有益，以及随着AGI部署，尽可能多的人都能受益。\
    OpenAI致力在商业利益和人类福祉之间做出正确的平衡，本质上是一家人道主义公司。\
    OpenAI开发了诸如GPT-3这样的先进模型，在自然语言处理等诸多领域表现出色。'

    # 第三个提示示例
    user_question3 = '围绕数据库中的user_payments表，我想要检查该表是否存在缺失值'
    user_message3_content = "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。" % user_question3
    assistant_message3_content = '为了检查user_payments数据集是否存在缺失值，我们将执行如下步骤：\
    \n\n步骤1：使用`extract_data`函数将user_payments数据表读取到当前的Python环境中。\
    \n\n步骤2：使用`python_inter`函数执行Python代码检查数据集的缺失值。'

    # 第四个提示示例
    user_question4 =  '我想寻找合适的缺失值填补方法，来填补user_payments数据集中的缺失值。'
    user_message4_content = "现有用户问题如下：“%s”。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。" % user_question4
    assistant_message4_content = '为了找到合适的缺失值填充方法，我们需要执行以下三步：\
    \n\n步骤1：分析user_payments数据集中的缺失值情况。通过查看各字段的缺失率和观察缺失值分布，了解其缺失幅度和模式。\
    \n\n步骤2：确定值填补策略。基于观察结果和特定字段的性质确定恰当的填补策略，例如使用众数、中位数、均值或建立模型进行填补等。\
    \n\n步骤3：进行缺失值填补。根据确定的填补策略，执行填补操作，然后验证填补效果。'
    # 在保留原始问题的情况下加入Few-shot
    task_decomp_few_shot = messages.copy()
    # task_decomp_few_shot.messages_pop(manual=True, index=-1)
    task_decomp_few_shot.messages_append({"role": "user", "content": user_message1_content})
    task_decomp_few_shot.messages_append({"role": "assistant", "content": assistant_message1_content})
    task_decomp_few_shot.messages_append({"role": "user", "content": user_message2_content})
    task_decomp_few_shot.messages_append({"role": "assistant", "content": assistant_message2_content})
    task_decomp_few_shot.messages_append({"role": "user", "content": user_message3_content})
    task_decomp_few_shot.messages_append({"role": "assistant", "content": assistant_message3_content})
    task_decomp_few_shot.messages_append({"role": "user", "content": user_message4_content})
    task_decomp_few_shot.messages_append({"role": "assistant", "content": assistant_message4_content})

    user_question = messages.history_messages[-1]["content"]

    new_question = "现有用户问题如下：“%s“。为了回答这个问题，总共需要分几步来执行呢？\
    若无需拆分执行步骤，请直接回答原始问题。" % user_question
    question_message = messages.history_messages[-1].copy()
    question_message["content"] = new_question
    task_decomp_few_shot.messages_append(question_message)

    return task_decomp_few_shot


def modify_prompt_fn(messages, action='add', enable_md_output=True, enable_COT=True):
    """
    当开启开发者模式时，会让用户选择是否添加COT提示模板或其他提示模板，并创建一个经过修改的新的message。
    :param messages:必要参数，ChatMessages类型对象，用户存储对话信息
    :param action: 'add' or 'remove'，决定添加还是移除提示
    :param enable_COT:是否启用COT提示
    :return: messages,一个经过提示词修改的message
    """

    # 思考链提示词模板
    cot_prompt = "请一步步思考并得出结论"

    # 输出markdown提示词模板
    md_prompt = "任何回答都请以markdown格式进行输出。"

    # 如果是添加提示词
    if action == 'add':
        if enable_COT:
            messages.messages[-1]['content'] += cot_prompt
            messages.history_messages[-1]['content'] += cot_prompt

        if enable_md_output:
            messages.messages[-1]["content"] += md_prompt
            messages.history_messages[-1]["content"] += md_prompt
    elif action == 'remove':
        if enable_md_output:
            messages.messages[-1]["content"] = messages.messages[-1]["content"].replace(md_prompt, "")
            messages.history_messages[-1]["content"] = messages.history_messages[-1]["content"].replace(md_prompt, "")
        
        if enable_COT:
            messages.messages[-1]["content"] = messages.messages[-1]["content"].replace(cot_prompt, "")
            messages.history_messages[-1]["content"] = messages.history_messages[-1]["content"].replace(cot_prompt, "")

    return messages

def get_gpt_response(txt,
                     chatbot,
                     md_dropdown, 
                     messages, 
                     available_functions=None,
                     modify_prompt=False,
                     add_task_decomposition=False):
    
    """
    负责调用Chat模型并获得模型回答函数，并且当在调用GPT模型时遇到Rate limit时可以选择暂时休眠1分钟后再运行。\
    同时对于意图不清的问题，会提示用户修改输入的prompt，以获得更好的模型运行结果。
    :param chatbot:WEBUI中显示的对话列表，yield出去可以直接修改对话
    :param md_dropdown: 必要参数，表示调用的大模型名称
    :param messages: 必要参数，ChatMessages类型对象，用于存储对话消息
    :param available_functions: 可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况。\
    默认为None，表示没有外部函数
    :param is_developer_mode: 表示是否开启开发者模式，默认为False。\
    开启开发者模式时，会自动添加提示词模板，并且会在每次执行代码前、以及返回结果之后询问用户意见，并会根据用户意见进行修改。
    :param is_enhanced_mode: 可选参数，表示是否开启增强模式，默认为False。\
    开启增强模式时，会自动启动复杂任务拆解流程，并且在进行代码debug时会自动执行deep debug。
    :return: 返回模型返回的response message
    """
    # 开启则进行提示词修改，首次运行是增加提示词
    if modify_prompt:
        messages = modify_prompt_fn(messages, action='add')
        
    # # 如果是，则增加复杂任务拆解流程
    # if add_task_decomposition:
    #     messages = add_task_decomposition_prompt_fn(messages)

    # 考虑到可能存在通信报错问题，因此循环调用Chat模型进行执行
    while True:
        try:
            # 若不存在外部函数
            if available_functions == None:
                response = openai.OpenAI().chat.completions.create(
                    model=md_dropdown,
                    messages=messages.messages)   
            # 若存在外部函数，此时functions和function_call参数信息都从AvailableFunctions对象中获取
            else:
                response = openai.OpenAI().chat.completions.create(
                    model=md_dropdown,
                    messages=messages.messages, 
                    functions=available_functions.functions, 
                    function_call=available_functions.function_call
                    )   
            break  # 如果成功获取响应，退出循环
        except Exception as e:
            print("发生了一个错误，报错信息如下:\n", e)
            break
    
    # 还原原始的msge对象
    if modify_prompt:
        messages = modify_prompt_fn(messages, action='remove')
    
    return response.choices[0].message, chatbot, md_dropdown, messages 

def function_to_call(available_functions, function_call_message):
    """
    根据一条函数调用消息function_call_message，返回一条函数运行结果消息function_response_messages.
    :param available_functions: 必要参数，要求输入一个AvailableFunctions对象，以说明当前外部函数基本情况
    :param function_call_message:必要参数，要求输入一条外部函数调用的message
    :return: function_response_messages，输出由外部函数所组成的message
    """

    # 获取调用外部函数的函数名称
    function_name = function_call_message.function_call.name

    # 根据函数名称获取对应的外部函数对象
    function_to_call = available_functions.functions_dic[function_name]

    # 提取function_call_message中调用外部函数的函数参数
    # 即大模型编写的Python代码
    function_args = json.loads(function_call_message.function_call.arguments)

    # 将参数带入到外部函数中运行
    try:
        # 将当前操作空间中的全局变量添加到外部函数中
        function_args['g'] = globals()

        # 运行外部函数
        function_response = function_to_call(**function_args)
    # 若外部函数运行报错，则提取报错信息
    except Exception as e:
        function_response = "函数运行报错如下：" + str(e)
        # print(function_response)
    # 创建function_response_messages
    # 该message包含外部函数顺利运行或报错信息

    function_response_messages = {
        "role": "function",
        "name": function_name,
        "content": function_response,
    }
    return function_response_messages

def get_chat_response(txt,
                      chatbot,
                      md_dropdown,
                      messages,
                      modify_prompt=False,
                      add_task_decomposition=False,
                      available_functions=None,
                      delete_some_messages=False,
                     ):
    """
    负责完整执行一次对话的最高层函数，需要注意的是，一次对话中可能会多次调用大模型，而本函数则是完成一次对话的主函数。\
    要求输入的messages中最后一条消息必须是能正常发起对话的消息。\
    该函数通过调用get_gpt_response来获取模型输出结果，并且会根据返回结果的不同，例如是文本结果还是代码结果,\
    灵活调用不同函数对模型输出结果进行后处理.\
    :param chatbot:WEBUI中显示的对话列表，yield出去可以直接修改对话
    :param md_dropdown:必要参数，表示调用的大模型名称
    :param messages:必要参数，ChatMessages类型对象，用于存储对话信息
    :param available_functions:可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况.\
    默认为None，表示没有外部函数
    :param is_developer_mode: 表示是否开启开发者模式，默认为False。\
    开启开发者模式后，会自动添加提示词模板，并且会在每次执行代码前，以及返回结果之后询问用户意见，并会根据用户意见进行修改.
    :param is_enhanced_mode:可选参数，表示是否开启增强模式，默认为False。\
    开启增强模式后时，会自动启动复杂任务拆解流程，并且在进行代码debug时会自动执行deep debug。
    :param delete_some_messages:可选参数，表示在拼接messages时是否删除中间若干条信息，默认为False。
    :param add_task_decomposition:可选参数，是否在当前执行任务时审查任务拆解结果，默认为False。
    :return: 拼接本次问答最终结果messages
    """
    chatbot.append((txt, None))
    yield from update_ui(txt, chatbot, md_dropdown, messages)
    txt = gr.Textbox(value="", interactive=False)
    

    messages.messages_append({'role': 'user', 'content': chatbot[-1][0]})
    print("User:\n", messages.messages[-1]["content"]+"\n")
    # chatbot.append(("adsfasdfas", None))
    # yield from update_ui(txt, chatbot, md_dropdown, messages)
    # 当且仅当围绕复杂任务拆解结果进行修改时，才会出现isadd_task_decomposition_prompt=True的情况
    # 当add_task_decomposition=True时，不再重新创建response_message
    if not add_task_decomposition:
        # 先获取单次大模型调用结果
        # 此时response_message是大模型调用返回的function_response_message
        response_message, chatbot, md_dropdown, messages = get_gpt_response(txt,chatbot,
                                            md_dropdown=md_dropdown,
                                            messages=messages,
                                            available_functions=available_functions,
                                            modify_prompt=modify_prompt,
                                            add_task_decomposition=add_task_decomposition)

    # 复杂条件判断，若add_task_decomposition=True,
    # 或者是增强模式且是执行function response任务时
    # 需要注意的是，当add_task_decomposition = True时，并不存在response_message对象)
    if add_task_decomposition or response_message.function_call:
        # 将add_task_decomposition修改为True,表示当前执行任务为复杂任务拆解
        add_task_decomposition = True
        # 在拆解任务时，将增加了任务拆解的few-shot-message命名为text_response_messages
        task_decomp_few_shot = add_task_decomposition_prompt_fn(messages)
        chatbot.append((None, "正在进行任务拆解，请稍后..."))
        yield from update_ui(txt, chatbot, md_dropdown, messages)
        # 同时更新response_message,此时response_message就是任务拆解之后的response
        response_message, chatbot, md_dropdown, messages = get_gpt_response(txt, chatbot,
                                            md_dropdown=md_dropdown,
                                            messages=task_decomp_few_shot,
                                            available_functions=available_functions,
                                            modify_prompt=False,
                                            add_task_decomposition=False)
        # 若拆分任务的提示无效，此时response_message有可能会再次创建一个function call message
        if response_message.function_call:
            chatbot.append((None, "当前任务无需拆解，可以直接运行"))
            yield from update_ui(txt, chatbot, md_dropdown, messages)

    # 若本次调用是由修改对话需求产生，则按照参数设置删除原始message中的若干条消息
    # 需要注意的是，删除中间若干条信息，必须在创建完新的response_message之后再执行
    if delete_some_messages:
        for i in range(delete_some_messages):
            messages.messages_pop(manual=True,index=-1)

    # 注意，执行到此处时，一定会有一个response_message
    # 接下来分response_message不同类型，执行不同流程
    # 若是文本响应类任务（包括普通文本响应和复杂任务拆解审查两种情况，都可以使用相同代码）

    if not response_message.function_call:
        # 将message保存为text_answer_message
        text_answer_message = response_message
        # 返回结果并带入is_text_response_valid对文本内容进行审查
        chatbot.append((None, text_answer_message.content))
        yield from update_ui(txt, chatbot, md_dropdown, messages)
    
        # 若是任务拆解
        if add_task_decomposition:

            for i in range(9):
                messages.messages_pop(manual=True,index=-1)

            # 任务拆解中，如果选择执行该流程
            messages.messages_append(text_answer_message)
            print("Model:\n", messages.messages[-1].content + '\n\n')
            # chatbot.append((None, "下面逐步执行上述流程"))
            # yield from update_ui(txt, chatbot, md_dropdown, messages)
            add_task_decomposition = False
            txt = "非常好，请按照该流程逐步执行。"
            chatbot.append((txt, None))
            yield from update_ui(txt, chatbot, md_dropdown, messages)
            messages.messages_append({'role': 'user', 'content': "好的，请对上述的每一个流程进行详细的描述"})
            print("User:\n", messages.messages[-1]["content"] + "\n")
            response_message, chatbot, md_dropdown, messages = get_gpt_response(txt, chatbot,
                                            md_dropdown=md_dropdown,
                                            messages=task_decomp_few_shot,
                                            available_functions=available_functions,
                                            modify_prompt=False,
                                            add_task_decomposition=False)
            
            if not response_message.function_call:
                text_answer_message = response_message
                # 返回结果并带入is_text_response_valid对文本内容进行审查
                chatbot.append((None, text_answer_message.content))
                txt = gr.Textbox(value="", interactive=False)
                yield from update_ui(txt, chatbot, md_dropdown, messages)
                messages.messages_append(text_answer_message)
                print("Model:\n", messages.messages[-1].content+"\n\n")
                    
 

        else:
            messages.messages_append(text_answer_message)
            print("Model:\n", messages.messages[-1].content+"\n\n")
        
    # 若是function response任务
    elif response_message.function_call:
        # 创建调用外部函数的function_call message
        # 在当前Agent中，function_call_message是一个包含Python代码的JSON对象
        function_call_message = response_message
        # 将function_call_message带入代码审查和运行函数is_code_response_valid
        # 并最终获得外部函数运行之后的问答结果
        messages = is_code_response_valid(txt,
                                          chatbot,
                                          md_dropdown=md_dropdown,
                                          messages=messages,
                                          function_call_message=function_call_message,
                                          available_functions=available_functions,
                                          is_developer_mode=is_developer_mode,
                                          is_enhanced_mode=is_enhanced_mode,
                                          delete_some_messages=delete_some_messages)

    return txt, chatbot, md_dropdown, messages

# 判断代码输出结果是否符合要求，输入function_call_message,输出function response message
def is_code_response_valid(txt,
                           chatbot,
                           md_dropdown,
                           messages,
                           function_call_message,
                           available_functions=None,
                           is_developer_mode=False,
                           is_enhanced_mode=False,
                           delete_some_messages=False):
    """
    负责完整执行一次外部函数调用的最高层函数，要求输入的msg最后一条消息必须是包含function_call的消息.\
    函数的最终任务是将function call的消息中的代码带入外部函数并完成代码运行，并且支持交互式代码编写或自动代码编写运行不同模式.\
    当函数运行得到一条包含外部函数运行结果的function message之后，会继续将其带入check_get_final_function_response函数，\
    用于最终将function message转化为assistant message,并完成本次对话。
    :param chatbot:WEBUI中显示的对话列表，yield出去可以直接修改对话
    :param md_dropdown:必要参数，调用的大模型名称
    :param messages:必要参数，ChatMessages类型对象,用于存储对话信息
    :param function_call_message:必要参数，用于表示上层函数创建的一条包含function call消息的message
    :param available_functions: 可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况.\
    默认为None,表示没有外部函数
    :param is_developer_mode: 表示是否开启开发者模式,默认为False。\
    开启开发者模式时，会自动添加提示词模板，并且会在每次执行代码前、以及返回结果之后询问用户意见，并会根据用户意见进行修改。
    :param is_enhanced_mode:可选参数，表示是否开启增强模式，默认为False。\
    开启增强模式后时，会自动启动复杂任务拆解流程，并且在进行代码debug时会自动执行deep debug。\
    :param delete_some_messages:可选参数，表示在拼接messages时是否删除中间若干条消息，默认为False.
    :return: message,拼接了最新大模型回答结果的message
    """
    # 为打印代码和修改代码（增加创建图像部分代码）做准备
    # 创建字符串类型json格式的message对象
    code_json_str = function_call_message.function_call.arguments
    # 将json转化为字典
    try:
        code_dict = json.loads(code_json_str)
    except Exception as e:
        chatbot.append((None, "json字符解析错误，正在重新创建代码..."))
        yield from update_ui(txt, chatbot, md_dropdown, messages)
        # 递归调用上层函数get_chat_response，并返回最终message结果
        # 需要注意的是，如果上层函数再次创建了function_call_message
        # 则会再次调用is_code_response_valid，而无需在当前函数中再次执行
        messages = get_chat_response(md_dropdown=md_dropdown, 
                                     messages=messages, 
                                     available_functions=available_functions,
                                     is_developer_mode=is_developer_mode,
                                     is_enhanced_mode=is_enhanced_mode, 
                                     delete_some_messages=delete_some_messages)
        return messages
    # 若顺利将json转化为字典，则继续执行下面代码
    # 创建convert_to_markdown内部函数，用于辅助打印代码结果
    def convert_to_markdown(code, language):
        return f"```{language}\n{code}\n```"
    # 提取代码部分参数
    if code_dict.get('py_code'):
        code = code_dict['py_code']
        markdown_code = convert_to_markdown(code, 'python')
        chatbot.append((None, "即将执行以下代码:"))
        yield from update_ui(txt, chatbot, md_dropdown, messages)
    else:
        markdown_code = code_dict
    chatbot.append((None, markdown_code))
    yield from update_ui(txt, chatbot, md_dropdown, messages)

    # 若是开发者模式，则提示用户先对代码进行审查然后再运行
    if is_developer_mode:
        user_input = input("直接运行代码（1），还是反馈修改意见，并让模型对代码进行修改后运行（2）")
        if user_input == '1':
            chatbot.append((None, "好的，正在运行代码，请稍后..."))
            yield from update_ui(txt, chatbot, md_dropdown, messages)
        else:
            modify_input = input("好的，请输入修改意见:")
            # 记录模型当前创建的代码
            messages.messages_append(function_call_message)
            # 记录修改意见
            messages.messages_append({"role": "user", "content": modify_input})
             
            # 调用get_chat_response函数并重新获取回答结果
            # 需要注意，此时需要设置delete_some_messages=2，删除中间对话结果以节省token
            txt, chatbot, md_dropdown, messages = get_chat_response(md_dropdown=md_dropdown, 
                                         messages=messages, 
                                         available_functions=available_functions,
                                         is_developer_mode=is_developer_mode,
                                         is_enhanced_mode=is_enhanced_mode, 
                                         delete_some_messages=2)
            
            return messages
    # 若不是开发者模式，或者开发者模式下user_input == '1'
    # 则调用function_to_call函数，并获取最终外部函数运行结果
    # 在当前Agent中，外部函数运行结果就是SQL或者Python运行结果，或代码运行报错结果
    function_response_message = function_to_call(available_functions=available_functions, 
                                                 function_call_message=function_call_message)  
    
    # 将function_response_message带入check_get_final_function_response进行审查
    messages = check_get_final_function_response(md_dropdown=md_dropdown, 
                                                 messages=messages, 
                                                 function_call_message=function_call_message,
                                                 function_response_message=function_response_message,
                                                 available_functions=available_functions,
                                                 is_developer_mode=is_developer_mode,
                                                 is_enhanced_mode=is_enhanced_mode, 
                                                 delete_some_messages=delete_some_messages)
    
    return messages                


# 判断代码输出结果是否符合要求，输入function response message,输出基于外部函数运行结果的message
def check_get_final_function_response(chatbot,
                                      md_dropdown,
                                      messages,
                                      function_call_message,
                                      function_response_message,
                                      available_functions=None,
                                      is_developer_mode=False,
                                      is_enhanced_mode=False,
                                      delete_some_messages=False):
    """
    负责执行外部函数运行结果审查工作。若外部函数运行结果消息function_response_message并不存在报错消息,
    则将其拼接入message中，并将其带入get_chat_response函数并获取下一轮对话结果。而如果function_response_message中存在报错消息,
    则开启自动debug模式，本函数将借助类似AutoGen的模式，复制多个Agent，并通过彼此对话的方式完成debug。
    :param chatbot:WEBUI中显示的对话列表，yield出去可以直接修改对话
    :param md_dropdown: 必要参数，表示调用的大模型名称
    :param messages: 必要参数，ChatMessages类型对象，用于存储对话消息
    :param function_call_message: 必要参数，用于表示上层函数创建的一条包含function call消息的message
    :param function_response_message: 必要参数，用于表示上层函数创建的一条包含外部函数运行结果的message
    :param available_functions: 可选参数，AvailableFunctions类型对象，用于表示开启对话时外部函数基本情况。\
    默认为None，表示没有外部函数
    :param is_developer_mode: 表示是否开启开发者模式，默认为False。\
    开启开发者模式时，会自动添加提示词模板，并且会在每次执行代码前、以及返回结果之后询问用户意见，并会根据用户意见进行修改。
    :param is_enhanced_mode: 可选参数，表示是否开启增强模式，默认为False。\
    开启增强模式时，会自动启动复杂任务拆解流程，并且在进行代码debug时会自动执行deep debug。
    :param delete_some_messages: 可选参数，表示在拼接messages时是否删除中间若干条消息，默认为Fasle。
    :return: message，拼接了最新大模型回答结果的message
    """    
    # 获取外部函数运行结果内容
    fun_res_content = function_response_message["content"]

    # 若function_response中包含错误
    if "报错" in fun_res_content:
        # 打印报错信息
        chatbot.append((None, fun_res_content))
        yield from update_ui(txt, chatbot, md_dropdown, messages)

        # 根据是否是增强模式，选择执行高效debug或深度debug
        # 高效debug和深度debug区别只在于提示内容和提示流程不同
        # 高效debug只包含一条提示，只调用一次大模型即可完成自动debug工作
        # 而深度debug则包含三次提示，需要调用三次大模型进行深度总结并完成debug工作
        # 先创建不同模式debug的不同提示词
        if not is_enhanced_mode:
            # 执行高效debug
            chatbot.append((None, "**即将执行高效debug，正在实例化Efficient Debug Agent...**"))
            yield from update_ui(txt, chatbot, md_dropdown, messages)
            
            debug_prompt_list = ["你编写的代码报错了，请根据报错信息修改代码并重新执行。"]
        else:
            # 执行深度debug
            chatbot.append((None, "**即将执行深度debug，该debug过程将自动执行多轮对话，请耐心等待。正在实例化Deep Debug Agent...**"))
            chatbot.append((None, "**正在实例化Deep Debug Agent...**"))
            yield from update_ui(txt, chatbot, md_dropdown, messages)
            
            debug_prompt_list = ["之前执行的代码报错了，你觉得代码哪里编写错了？", 
                                 "好的。那么根据你的分析，为了解决这个错误，从理论上来说，应该如何操作呢？", 
                                 "非常好，接下来请按照你的逻辑编写相应代码并运行。"]

        # 复制msg，相当于创建一个新的Agent进行debug
        # 需要注意的是，此时msg最后一条消息是user message，而不是任何函数调用相关message
        msg_debug = messages.copy()
        # 追加function_call_message
        # 当前function_call_message中包含编错的代码
        msg_debug.messages_append(function_call_message)
        # 追加function_response_message
        # 当前function_response_message包含错误代码的运行报错信息
        msg_debug.messages_append(function_response_message)

        # 依次输入debug的prompt，来引导大模型完成debug
        for debug_prompt in debug_prompt_list:
            msg_debug.messages_append({"role": "user", "content": debug_prompt})
            
            chatbot.append((None, "**From Debug Agent:**"))
            chatbot.append((None, debug_prompt))
            yield from update_ui(txt, chatbot, md_dropdown, messages)

            # 再次调用get_chat_response,在当前debug的prompt下，get_chat_response会返回修改意见或修改后的代码
            # 打印提示信息
            chatbot.append((None, "**From DieBian:**"))
            yield from update_ui(txt, chatbot, md_dropdown, messages)

            msg_debug = get_chat_response(md_dropdown=md_dropdown, 
                                          messages=msg_debug, 
                                          available_functions=available_functions,
                                          is_developer_mode=is_developer_mode,
                                          is_enhanced_mode=False, 
                                          delete_some_messages=delete_some_messages)
        messages = msg_debug.copy()

    
    # 若function message不包含报错信息    
    # 需要将function message传递给模型
    else:
        chatbot.append((None, "外部函数已执行完毕，正在解析运行结果..."))
        yield from update_ui(txt, chatbot, md_dropdown, messages)

        messages.messages_append(function_call_message)
        messages.messages_append(function_response_message)
        messages = get_chat_response(md_dropdown=md_dropdown, 
                                     messages=messages, 
                                     available_functions=available_functions,
                                     is_developer_mode=is_developer_mode,
                                     is_enhanced_mode=is_enhanced_mode, 
                                     delete_some_messages=delete_some_messages)
        
    return messages