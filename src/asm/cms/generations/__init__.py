import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=8,
    generation=8,
    package_name='asm.cms.generations')
