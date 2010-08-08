# Copyright (c) 2010 gocept gmbh & co. kg
# See also LICENSE.txt

class Index(megrok.pagelet.Pagelet):
    grok.layer(asm.cms.interfaces.IRetailSkin)


class Edit(asm.cms.form.EditionEditForm):

    grok.layer(asm.cms.interfaces.ICMSSkin)
    grok.require('asm.cms.EditContent')

    main_fields = grok.AutoFields(HTMLPage).select(
        'title', 'content')
    main_fields['content'].custom_widget = asm.cms.tinymce.TinyMCEWidget

    def post_process(self):
        self.content = fix_relative_links(
            self.context.content, self.url(self.context))

class SearchPreview(grok.View):

    PREVIEW_AMOUNT = 50

    def update(self, q):
        self.keyword = q

    def render(self):
        try:
            tree = lxml.etree.fromstring(
                '<stupidcafebabe>%s</stupidcafebabe>' % self.context.content)
        except Exception:
            return ''
        text = ''.join(tree.itertext())

        # Select limited amount of characters
        focus = text.lower().find(self.keyword.lower())
        if focus == -1:
            return cgi.escape(text[:2*self.PREVIEW_AMOUNT])
        text = text[
            max(focus - self.PREVIEW_AMOUNT, 0):(focus + self.PREVIEW_AMOUNT)]

        # Insert highlighting. Recompute offset of focus with shorter text.
        focus = text.lower().find(self.keyword.lower())
        pre, keyword, post = (text[:focus],
                              text[focus:focus + len(self.keyword)],
                              text[focus + len(self.keyword):])
        text = '%s<span class="match">%s</span>%s' % \
            tuple(map(cgi.escape, [pre, keyword, post]))
        return text

