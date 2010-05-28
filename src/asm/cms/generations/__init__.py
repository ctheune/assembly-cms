import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=4,
    generation=4,
    package_name='asm.cms.generations')
