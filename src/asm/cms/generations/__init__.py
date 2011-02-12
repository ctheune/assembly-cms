import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=7,
    generation=7,
    package_name='asm.cms.generations')
