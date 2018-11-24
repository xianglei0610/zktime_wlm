# coding=utf-8
'''
删除指纹模板: OpDeleteTemplate
下发用户照片: PushUserPhoto
删除设备用户照片: DeleteUserPhoto
下发用户面部模板: PushUserFace
删除设备用户面部模板: DeleteUserFace
'''
from mysite.personnel.models.model_emp import Employee,format_pin,device_pin,del_fp
from django.conf import settings
from django import forms
import datetime
from traceback import print_exc
from base.operation import ModelOperation,Operation
from django.utils.translation import ugettext_lazy as _

def get_device_from_emp(emp):
    attarea = emp.attarea.all()
    devices = []
    for e in attarea:
        devices+=e.device_set.all()
    return devices

def append_dev_cmd(dev,CmdContent):
    from mysite.iclock.models import DevCmd
    import datetime
    devcmd=DevCmd(SN=dev ,CmdContent=CmdContent,CmdCommitTime=datetime.datetime.now())
    devcmd.save()

def append_emp_cmd(emp,cmd):
    attarea = emp.attarea.all()
    if attarea:
        for atta in attarea:
            dvs = atta.device_set.all()
            if dvs:
                for dv in  dvs :
                     append_dev_cmd(dv,cmd)
                     
def append_emp_delface_cmd(emp,cmd):
    attarea = emp.attarea.all()
    if attarea:
        for atta in attarea:
            dvs = atta.device_set.all()
            if dvs:
                for dv in  dvs :
                    if dv.push_status[0]=='1' and dv.push_status[2]=='1':
                        append_dev_cmd(dv,cmd)
    
def append_emp_face_cmd(emp,cmd,face):
    attarea = emp.attarea.all()
    if attarea:
        for atta in attarea:
            dvs = atta.device_set.all()
            if dvs:
                for dv in  dvs :
                    from mysite.iclock.models import FaceTemplate
                    faces_count = FaceTemplate.objects.filter(user=emp.id,face_ver=dv.face_ver).count()
                    if dv.face_tmp_count == faces_count and face.face_ver ==dv.face_ver and dv.push_status[0]=='1' and dv.push_status[2]=='1':
                        append_dev_cmd(dv,cmd)
    
def sendphoto_deive(user):
    u'''
    下发人员相片到设备---传值过来的是人员对象
    '''
    from mysite.iclock.models import DevCmd
    import base64
    e=user#Employee.objects.filter(PIN=pin)[0]
    if e.photo:
        f = open(e.photo.file.name,'rb')#base64.b64encode(f.read())
        base64_photo=base64.b64encode(f.read())
        f.close()
        len_photo = len(base64_photo)
        if len_photo>16*1024/0.75:
            return  _(u'人员照片大小不能超过16Kb')
        attarea = e.attarea.all()
        data="DATA UPDATE USERPIC PIN=%s\tSize=%s\tContent=%s\t"%(device_pin(e.PIN),str(len_photo),base64_photo)
        if attarea:
            for atta in attarea:
                dvs = atta.device_set.all()
                if dvs:
                    for dv in  dvs : 
                        if dv.push_status[0]=='1' and dv.push_status[3]=='1':  
                            devcmd=DevCmd(SN=dv,CmdContent=data,CmdCommitTime=datetime.datetime.now())
                            devcmd.save(force_insert=True)
        return  None
    else:
        return  _(u'该人员未上传照片')
    
def delete_dev_user_photo(emp):
    '''
    下发删除设备上的人员照片
    '''
    from mysite.iclock.models import DevCmd
    e=emp
    data="DATA DELETE USERPIC PIN=%s\t"%(device_pin(e.PIN))
    attarea = e.attarea.all()
    if attarea:
        for arra in attarea:
            dvs = arra.device_set.all()
            if dvs:
                for dv in dvs:
                    if dv.push_status[0]=='1' and dv.push_status[3]=='1':
                        devcmd=DevCmd(SN=dv,CmdContent=data,CmdCommitTime=datetime.datetime.now())
                        devcmd.save(force_insert=True)
                    
def get_face_from_emp(emp):
    from mysite.iclock.models import FaceTemplate
    try:
        faces = FaceTemplate.objects.filter(user=emp.id)
        if faces:
            return  faces
        else:
            return  []
    except:
        return []
                    
def send_dev_face(emp,dvs=None):
    if dev is None:
        dvs = get_device_from_emp(emp)
    faces = get_face_from_emp(emp)
    faces_count = len(faces)
    for face in faces:   
        if faces_count>0:
            line = "PIN=%s\tFID=%d\tSIZE=%d\tValid=%d\tTMP=%s"%(device_pin(face.user.PIN), face.faceid,len(face.facetemp),face.valid, face.facetemp)
            CMD="DATA UPDATE FACE %s"%(line)
            append_emp_face_cmd(emp,CMD,face)
                
def delete_dev_face(emp):
    cmd = 'DATA DELETE FACE PIN=%s'%device_pin(emp.PIN)
    append_emp_delface_cmd(emp,cmd)
    
class PushUserPhoto(Operation):
    help_text = _(u"""下发用户照片""")
    verbose_name = _(u"""下发用户照片""")
    visible = False
    def action(self):
        msg = sendphoto_deive(self.object)
        if msg:
            raise Exception(msg)
        
class DeleteUserPhoto(Operation):
    help_text = _(u"""删除用户照片""")
    verbose_name = _(u"""删除用户照片""")
    visible = False
    def action(self):
        delete_dev_user_photo(self.object)
        
class PushUserFace(Operation):
    help_text = _(u"""下发用户面部模板""")
    verbose_name = _(u"""下发面部模板""")
    visible = False
    def action(self):
        send_dev_face(self.object)
        
class DeleteUserFace(Operation):
    help_text = _(u"""删除设备用户面部模板""")
    verbose_name = _(u"""删除面部模板""")
    def action(self):
       from base.sync_api import SYNC_MODEL
       if SYNC_MODEL:
           from base.sync_api import delete_emp_fc
           delete_emp_fc(self.object.PIN)
       else:
           delete_dev_face(self.object)
        
class OpDeleteTemplate(Operation):
       verbose_name=_(u"删除指纹模板")
       only_one_object = True
       help_text=_(u"删除指定的指纹模板,同时下发到设备")
#       params=(
#               ('tmps', forms.MultipleChoiceField(_(u'选择指纹模板'),widget=forms.CheckboxSelectMultiple,required=False)),
#               )
       def __init__(self, obj):
           super(Employee.OpDeleteTemplate, self).__init__(obj)
#           params=dict(self.params)
#           tmps=params['tmps']
#           tmps.label=_(u'选择指纹模板')
#           from mysite.iclock.models import Template
#           tmps.choices=tuple([(i.id,u""+i.get_FingerID_display()+u" ("+i.Fpversion+u"版本)") for i in Template.objects.filter(UserID=obj.PIN)])
#           
#           params['tmps']=tmps
#           self.params=tuple(params.items())
       def action(self):
           from base.sync_api import SYNC_MODEL
           if SYNC_MODEL:
               from base.sync_api import delete_emp_fp
               delete_emp_fp(self.object.PIN)
           else:
               from mysite.iclock.models import Template,Device
#               if not tmps:
#                   return#raise Exception (_(u"请选择需要删除的指纹模板!"))
#               del_fp(self.object,tmps)

Employee.OpDeleteTemplate = OpDeleteTemplate
            
Employee.PushUserPhoto = PushUserPhoto
Employee.DeleteUserPhoto = DeleteUserPhoto
Employee.PushUserFace = PushUserFace
Employee.DeleteUserFace = DeleteUserFace