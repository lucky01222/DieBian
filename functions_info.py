# 大模型能够调用的外部函数库的JsonSchema对象信息，记录了该函数的功能，用于输入大模型让其知晓函数的功能

python_inter_function_info = {
    'name': 'python_inter',
    'description': '专门用于执行非绘图的python代码，并获取最终查询或处理结果。若是需要执行绘图操作的Python代码，请勿调用python_inter函数，而请直接调用fig_inter函数来完成任务。',
    'parameters': {
        'type': 'object',
        'properties': {
            'py_code': {
                'type': 'string',
                'description': '用于执行非绘图操作的python代码，若要执行绘图，请用fig_inter函数'
            },
            'g': {
                'type': 'string',
                'description': '环境变量，可选参数，保持默认参数即可'
            }
        },
        'required': ['py_code']
    }
}

fig_inter_function_info = {
    'name': 'fig_inter',
  'description': '用于执行一段包含可视化绘图的Python代码，并最终获取一个图片类型对象',
  'parameters': {
      'type': 'object',
      'properties': {'py_code': {'type': 'string',
      'description': '代码中必须包含Figure对象创建过程'},
      },
   'required': ['py_code']}}