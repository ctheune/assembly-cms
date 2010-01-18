import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=2,
    generation=2,
    package_name='asm.cms.generations')
