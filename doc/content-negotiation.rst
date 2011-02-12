===================
Content negotiation
===================

Goals:

1. Content will contain relative links to *pages*
2. URLs should be portable: handing a URL to a different user should result in
   a version shown to him that fits his requirements (language, content type,
   editing state) thus URLs need to be free of content negotiation arguments
3. URLs also need to be stable, e.g. for the CMS edi
4. CMS editing and retail view should share the same way of talking about
   resources.

What is a resource?

Probably right

1. We manage pages
2. Links point to pages
3. Visiting a page means accessing that pages URL and retrieving an
   appropriate edition
4. Links never point to editions
5. Editing an edition requires to spell it's URL. We set a base tag to fix
   relative links, though

Corollary: 

Links stored in the content must not include the host. they may be absolute to
the domain, but I think they should be relative to allow out-of-scope (higher
up in the tree) virtual hosting changes without screwing up.

Also, if we store them relative, we can relatively easily make them absolute
when rendering the page to the outside (not in the editor though).


Maybe Good ideas

- URLs always refer to *pages* not editions
- URLs always refer to *editions* not pages
- Accessing a page's URL will result in a content-negotation strategy to be
  invoked which will determine which edition to use
- Use HTTP header ways: cookies (but not sessions), accept-*



Maybe Bad Ideas

- Encoding edition parameters in URLs makes them not portable (2) (both when
  selecting specific editions and encoding parameters in the beginning of the
  path)
- Sessions: makes the parameter invisible in the request and hinders caching
- URLs both referring to pages and editions?

Cons

- Communication about a specific edition needs to include data not found in
  the URL. This adds burden for developers/administrators but trades this for
  simplicity for end-users.




Open issues:

- How are temporal changes to an edition reflected?

  -> outside of the page's editions. make a new page with a different name.
     changes to a page using drafts is merely updating an existing resource.

- We should always return an edition, not a page, to avoid structural
  differences when no edition exists. In that case a NullEdition (like WebDAV)
  might be the right way.
