from invoke import run, task

@task
def antlr4(context):
    run("antlr4 -Dlanguage=Python3 -package gsl.grammar -visitor -no-listener gsl/grammar/GSL.g4")
