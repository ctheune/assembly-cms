# Copyright (c) 2008-2009 Assembly Organizing
# See also LICENSE.txt

import grok
import megrok.pagelet
import os.path
import zope.app.container.interfaces
import zope.event
import zope.lifecycleevent
import zope.traversing.api


class Form(megrok.pagelet.component.FormPageletMixin, grok.Form):

    grok.baseclass()
    template = grok.PageTemplateFile(os.path.join("templates", "form.pt"))
    extra_content = None


class BasicAddForm(megrok.pagelet.component.FormPageletMixin, grok.AddForm):

    grok.baseclass()
    template = grok.PageTemplateFile(os.path.join("templates", "form.pt"))
    extra_content = None

    # Needs to be set by the child class
    factory = None

    @grok.action("Add")
    def createAndAdd(self, **data):
        self.target = self.context
        obj = self.create(**data)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.applyData(obj, **data)
        self.add(obj)
        self.redirect(self.url(self.target))

    def add(self, obj):
        name = self.chooseName(obj)
        self.context[name] = obj

    def create(self, **data):
        return self.factory()

    def chooseName(self, obj):
        chooser = zope.app.container.interfaces.INameChooser(self.context)
        return chooser.chooseName('', obj)

    @property
    def form_fields(self):
        return grok.AutoFields(self.factory)



class BasicEditForm(megrok.pagelet.component.FormPageletMixin, grok.EditForm):

    grok.baseclass()
    template = grok.PageTemplateFile(os.path.join("templates", "form.pt"))
    extra_content = None
    redirect_to_parent = False

    @grok.action("Apply")
    def handle_edit_action(self, **data):
        super(BasicEditForm, self).handle_edit_action.success(data)
        if not self.errors:
            self.flash(self.status)
            if self.redirect_to_parent:
                target = zope.traversing.api.getParent(self.context)
            else:
                target = self.context
            self.redirect(self.url(target))


AddForm = BasicAddForm
EditForm = BasicEditForm
