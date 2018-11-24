# -*- coding: utf-8 -*-

'''
用于构建Mole系统模型页面架构
'''
##################### 系统环境设置 #######################
def set_lib_path():
    import sys
    import os
    sys.path.append('E:/custom_work/Mole')
    #os.environ["PYTHONPATH"]='../'
set_lib_path()

import mole.const
mole.const.ERROR_PAGE_TEMPLATE = """
%try:
    %from mole import DEBUG, HTTP_CODES, request
    %status_name = HTTP_CODES.get(e.status, 'Unknown').title()
             {"statusCode":"300", "message":'
            <title>ops! Error {{e.status}}: {{status_name}}</title>

            <h1>ops! Error {{e.status}}: {{status_name}}</h1>
            <p>Sorry, the requested URL <tt>{{request.url}}</tt> caused an error:</p>
            <pre>{{str(e.output)}}</pre>
            %if DEBUG and e.exception:
              <h2>Exception:</h2>
              <pre>{{repr(e.exception)}}</pre>
            %end
            %if DEBUG and e.traceback:
              <h2>Traceback:</h2>
              <pre>{{e.traceback}}</pre>
            %end
            '}
%except ImportError:
    <b>ImportError:</b> Could not generate the error page. Please add mole to sys.path
%end
"""



####################### 全局初始化 #######################

from load import ModelScan
ModelScan()

import route_func