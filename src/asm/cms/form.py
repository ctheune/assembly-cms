# Copyright (c) 2008-2009 Assembly Organizing
# See also LICENSE.txt

import asm.cms.interfaces
import grok
import megrok.pagelet
import os.path
import zope.app.container.interfaces
import zope.event
import zope.lifecycleevent
import zope.traversing.api


class CMSForm(object):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    template = grok.PageTemplateFile(os.path.join("templates", "form.pt"))

    @property
    def side_widgets(self):
        for w in self.widgets:
            if getattr(w, 'location') == 'side':
                yield w

    @property
    def main_widgets(self):
        for w in self.widgets:
            if getattr(w, 'location') != 'side':
                yield w

    def setUpWidgets(self, ignore_request=False):
        super(CMSForm, self).setUpWidgets(ignore_request)
        for widget in self.widgets:
            setattr(widget, 'location',
                    getattr(self.form_fields[widget.context.__name__], 'location', None))


class Form(CMSForm, megrok.pagelet.component.FormPageletMixin, grok.Form):

    grok.baseclass()


class AddForm(CMSForm, megrok.pagelet.component.FormPageletMixin, grok.AddForm):

    grok.baseclass()

    # Needs to be set by the child class
    factory = None

    @grok.action("Add")
    def createAndAdd(self, **data):
        self.target = self.context
        obj = self.create(**data)
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.applyData(obj, **data)
        self.add(obj)
        self.redirect(self.url(self.target, '@@edit'))

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


class EditForm(CMSForm, megrok.pagelet.component.FormPageletMixin, grok.EditForm):

    grok.baseclass()

    @grok.action("Save")
    def handle_edit_action(self, **data):
        super(EditForm, self).handle_edit_action.success(data)
        if self.errors:
            return
        self.flash(self.status)
        self.redirect(self.url(self.context, 'edit'))
