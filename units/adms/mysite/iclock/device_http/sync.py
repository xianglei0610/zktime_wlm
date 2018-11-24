# coding=utf-8

def update_info(pin,info_dic):
    pass
    return 0

def update_area(pin,area_list):
    pass
    return 0

def update_FingerPrint(pin,data):
    pass
    return 0

def update_HeadPortrait(pin,data):
    pass
    return 0

def update_face(pin,data):
    pass
    return 0

SyncType = dict([(element, index) for index, element in enumerate(('info', 'area', 'fp','pic','face'))])

def sync_employee(emp_obj,type=0):
    if type==SyncType.info:
        info = {'name':emp_obj.name,'card':emp_obj.card,'password':emp_obj.password}
        ret = update_area(emp_obj.PIN,info)
    if type==SyncType.area:
        ret = update_area(emp_obj.PIN,emp_obj.area)
    if type==SyncType.fp:
        ret = update_area(emp_obj.PIN,emp_obj.FingerPrint)
    if type==SyncType.pic:
        ret = update_area(emp_obj.PIN,emp_obj.HeadPortrait)
    if type==SyncType.face:
        ret = update_area(emp_obj.PIN,emp_obj.face)
    return ret
