from gsl import pseudo_tuple

from gsl.antlr import ParseTreeVisitor
if __name__ is not None and "." in __name__:
    from .G4VisitorParser import G4VisitorParser
else:
    from G4VisitorParser import G4VisitorParser


Visitor = pseudo_tuple('Visitor', ('name', 'grammar', 'rules',))
Rule = pseudo_tuple('Rule', ('name', 'body',))
ObjectBody = pseudo_tuple('ObjectBody', ('name', 'params',))
ObjectParam = pseudo_tuple('ObjectParam', ('name', 'expr', 'optional',))
ListItem = pseudo_tuple('ListItem', ('expr', 'optional',))
DictItem = pseudo_tuple('DictItem', ('name', 'expr', 'optional',))
RuleExpr = pseudo_tuple('RuleExpr', ('rules', 'multi', 'presence',))
TokenExpr = pseudo_tuple('TokenExpr', ('token', 'multi', 'presence',))
RefExpr = pseudo_tuple('RefExpr', ('ref', 'presence',))


class G4VVisitor(ParseTreeVisitor):
    def visitVisitor(self, ctx: G4VisitorParser.VisitorContext):
        return Visitor(
            self.visitNode(ctx.name),
            self.visitNode(ctx.grammarName),
            self.visitNodes(self.get_children(ctx, G4VisitorParser.VisitorRuleContext)),
        )

    def visitVisitorRule(self, ctx: G4VisitorParser.VisitorRuleContext):
        return Rule(
            self.visitNode(self.get_child(ctx, G4VisitorParser.RuleNameContext)),
            self.visitNode(self.get_child(ctx, G4VisitorParser.BodyContext)),
        )

    def visitExprBody(self, ctx: G4VisitorParser.ExprBodyContext):
        return self.visitNode(self.get_child(ctx, G4VisitorParser.ExprContext))

    def visitObjectBody(self, ctx: G4VisitorParser.ObjectBodyContext):
        return ObjectBody(
            self.visitNode(self.get_child(ctx, G4VisitorParser.IdentifierContext)),
            self.visitNodes(self.get_children(ctx, G4VisitorParser.ObjectParamContext)),
        )

    def visitListBody(self, ctx: G4VisitorParser.ListBodyContext):
        return self.visitNodes(self.get_children(ctx, G4VisitorParser.ListItemContext))

    def visitDictBody(self, ctx: G4VisitorParser.DictBodyContext):
        return self.visitNodes(self.get_children(ctx, G4VisitorParser.DictItemContext))

    def visitObjectParam(self, ctx: G4VisitorParser.ObjectParamContext):
        return ObjectParam(
            self.visitNode(self.get_child(ctx, G4VisitorParser.IdentifierContext)),
            self.visitNode(self.get_child(ctx, G4VisitorParser.ExprContext)),
            bool(ctx.LBRACKET()),
        )

    def visitListItem(self, ctx: G4VisitorParser.ListItemContext):
        return ListItem(
            self.visitNode(self.get_child(ctx, G4VisitorParser.ExprContext)),
            bool(ctx.LBRACKET()),
        )

    def visitDictItem(self, ctx: G4VisitorParser.DictItemContext):
        return DictItem(
            self.visitNode(self.get_child(ctx, G4VisitorParser.IdentifierContext)),
            self.visitNode(self.get_child(ctx, G4VisitorParser.ExprContext)),
            bool(ctx.LBRACKET()),
        )

    def visitRuleExpr(self, ctx: G4VisitorParser.RuleExprContext):
        return RuleExpr(
            self.visitNodes(self.get_children(ctx, G4VisitorParser.RuleNameContext)),
            bool(ctx.STAR()),
            bool(ctx.QUESTION()),
        )

    def visitTokenExpr(self, ctx: G4VisitorParser.TokenExprContext):
        return TokenExpr(
            self.visitNode(self.get_child(ctx, G4VisitorParser.TokenNameContext)),
            bool(ctx.STAR()),
            bool(ctx.QUESTION()),
        )

    def visitRefExpr(self, ctx: G4VisitorParser.RefExprContext):
        return RefExpr(
            self.visitNode(self.get_child(ctx, G4VisitorParser.AttributeRefContext)),
            bool(ctx.QUESTION()),
        )

    def visitLcName(self, ctx: G4VisitorParser.LcNameContext):
        return self.visitNode(self.get_child(ctx))

    def visitUcName(self, ctx: G4VisitorParser.UcNameContext):
        return self.visitNode(self.get_child(ctx))

    def visitIdentifier(self, ctx: G4VisitorParser.IdentifierContext):
        return self.visitNode(self.get_child(ctx))

    def visitRuleName(self, ctx: G4VisitorParser.RuleNameContext):
        return self.visitNode(self.get_child(ctx))

    def visitTokenName(self, ctx: G4VisitorParser.TokenNameContext):
        return self.visitNode(self.get_child(ctx))

    def visitAttributeRef(self, ctx: G4VisitorParser.AttributeRefContext):
        return self.visitNode(self.get_child(ctx))

