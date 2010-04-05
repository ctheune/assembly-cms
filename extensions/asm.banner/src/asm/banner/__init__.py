import zope.deferredimport

zope.deferredimport.define(
    WORKFLOW_PUBLIC='asm.workflow.workflow:WORKFLOW_PUBLIC',
    WORKFLOW_DRAFT='asm.workflow.workflow:WORKFLOW_DRAFT',
    publish='asm.workflow.workflow:publish',
    )
