#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
生成实体关系(ER)图
"""

from django.template import Context, Template, loader, TemplateDoesNotExist

def get_entify_content(model):
        pk=[model._meta.pk]
        fields=[]
        for f in model._meta.fields:
                if f == model._meta.pk:
                        pass
                else:
                        fields.append(f)
        return Context({'db_table': model._meta.db_table, 'pk': pk, 'fields': fields})

def entity_diagram(model):
        default_template='"{{ db_table }}" [ style = "filled" penwidth = 1 fillcolor = "white" fontname = "Courier New" shape = "Mrecord" label =<<table border="0" cellborder="0" cellpadding="3" bgcolor="white"><tr><td bgcolor="black" align="center" colspan="2"><font color="white">{{ db_table }}</font></td></tr>{% for f in pk %}<tr><td align="left" bgcolor="gray">{% firstof f.db_column f.name %}</td><td align="right" bgcolor="gray">{{ f.db_type }}</td></tr>{% endfor %}{% for f in fields %}<tr><td align="left">{% firstof f.db_column f.name %}</td><td align="right">{{ f.db_type }}</td></tr>{% endfor %}</table>> ];\n'
        try:
                t=loader.select_template(["entity_%s.dot"%model.__name__,"entity.dot"])
        except TemplateDoesNotExist:
                t=Template(default_template)
        return t.render(get_entify_content(model))

default_project_er_template="""
digraph g {
  graph [fontsize=30 labelloc="t" label="" splines=true overlap=false rankdir = "LR"];
  ratio = auto;
  {% for app in applications %}{{ app }}{% endfor %}
  {% for entity in entities %}{{ entity }}{% endfor %}
  {% for relation in relations %}{{ relation }}{% endfor %}
}"""

default_relation_template="""{{ table1 }} -> {{ table2 }} [ penwidth = 2 fontsize = 20 fontcolor = "gray" label = "{{ name }}" ];\n"""

def render_relation(relation):
        t=Template(default_relation_template)
        return t.render(Context({
                "table1": relation[1].db_table,
                "table2": relation[2].db_table,
                "name":relation[0].name}))

default_application_template="""subgraph cluster_{{ app_label }} {
        {% for m in models %}{{ m.db_table }};
        {% endfor %}
        label = "{{ app_label }}";
        color=blue;
        fontcolor = blue;
}
"""

def render_application(app):
        t=Template(default_application_template)
        return t.render(Context({
                "app_label": app[0],
                "models": app[1],
                }))
        

def project_entity_content():
        from django.conf import settings
        from base.translation import DataTranslation, _ugettext_ as _
        from django.contrib.contenttypes.models import ContentType
        from django.db.models.loading import get_app
        from django.db import models
        from django.core.urlresolvers import reverse
        model_list=[]
        relations=[]
        apps=[]
        for application in settings.INSTALLED_APPS:
                app_label=application.split(".")[-1]
                if app_label in ("admin","sessions"): continue
                app=get_app(app_label)
                ms=[]
                for i in dir(app):
                        try:
                                model=app.__getattribute__(i)
                                if issubclass(model, models.Model) and not model._meta.abstract and model._meta.app_label==app_label:
                                                model_list.append(model)
                                                for f in model._meta.fields:
                                                        if isinstance(f, models.ForeignKey):
                                                                relations.append((f, model._meta, f.rel.to._meta))
                                                ms.append(model._meta)
                        except: pass
                apps.append((app_label,ms))
        t=Context({"entities": [entity_diagram(model) for model in model_list], 
                "relations":[render_relation(relation) for relation in relations],
                "applications": [render_application(app) for app in apps],
                })
        return t

def project_entity_diagram(file_name=None):
        try:
                t=loader.select_template(["project_er.dot"])
        except TemplateDoesNotExist:
                t=Template(default_project_er_template)
        s=t.render(project_entity_content())
        if not file_name: return s
        f=file(file_name+".dot", "w+")
        f.write(s)
        f.close()
        import os
        os.system("dot -T%s %s.dot -o %s"%(os.path.splitext(file_name)[1][1:] or "png", file_name, file_name))
        os.system("rm %s.dot"%file_name)

if __name__=="__main__":
        try:
                import sys, os
                sys.path.append(os.getcwd())
        except ImportError, e:
                import sys
                raise e
        os.environ['DJANGO_SETTINGS_MODULE']='mysite.settings'
        project_entity_diagram(len(sys.argv)<2 and "entity-relation.png" or sys.argv[1])


