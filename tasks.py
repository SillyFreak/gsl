from invoke import run, task

@task
def antlr4(context):
    run("antlr4 -Dlanguage=Python3 -package gsl.grammar -visitor -no-listener gsl/grammar/GSL.g4 gsl/grammar/G4Visitor.g4")

@task
def g4v(context):
    run("g4v gsl/grammar/G4VisitorVisitor.g4v")

@task
def antlr4_tests(context):
    run("antlr4 -Dlanguage=Python3 -package grammar -visitor -no-listener tests/grammar/SetTest.g4 tests/grammar/ExprTest.g4 tests/grammar/HedgehogTest.g4")

@task
def g4v_tests(context):
    run("g4v tests/grammar/ExprTestVisitor.g4v tests/grammar/HedgehogTestVisitor.g4v tests/grammar/SetTestVisitor.g4v")
