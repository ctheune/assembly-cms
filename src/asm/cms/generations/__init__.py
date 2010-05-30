import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=5,
    generation=5,
    package_name='asm.cms.generations')
