import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=6,
    generation=6,
    package_name='asm.cms.generations')
