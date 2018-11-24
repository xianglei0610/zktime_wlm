# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

from models import VideoPreviewPage, VideoLinkagePage

verbose_name = _(u"视频")
_menu_index = 5

def app_options():
    from base.options import SYSPARAM, PERSONAL
    return (
    #参数名称, 参数默认值，参数显示名称，解释
        ('video_default_page', 'video/VideoPreviewPage/', u"%s"%_(u'视频默认页面'), "", PERSONAL, False),
    )

