import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=0,
    generation=0,
    package_name='asm.cms')
