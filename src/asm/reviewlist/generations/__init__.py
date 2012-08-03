import zope.app.generations.generations


manager = zope.app.generations.generations.SchemaManager(
    minimum_generation=1,
    generation=1,
    package_name='asm.reviewlist.generations')
