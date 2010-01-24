import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=3,
    generation=3,
    package_name='asm.cms.generations')
