import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=9,
    generation=9,
    package_name='asm.cms.generations')
