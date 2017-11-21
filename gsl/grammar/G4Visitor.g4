grammar G4Visitor;

visitor:
  VISITOR name=identifier FOR GRAMMAR grammarName=identifier SEMI
  visitorRule* EOF;

visitorRule: ruleName EQUALS body SEMI;

body:
  expr # exprBody |
  identifier LPAREN (objectParam (COMMA objectParam)* COMMA?)? RPAREN #objectBody |
  LBRACKET (listItem (COMMA listItem)* COMMA?)? RBRACKET #listBody |
  LBRACE (dictItem (COMMA dictItem)* COMMA?)? RBRACE #dictBody;

objectParam:
  identifier EQUALS expr |
  identifier EQUALS LBRACKET expr RBRACKET;

listItem:
  expr |
  LBRACKET expr RBRACKET;

dictItem:
  identifier COLON expr |
  identifier COLON LBRACKET expr RBRACKET;

expr:
  ((DOT | ruleName | LPAREN ruleName (OR ruleName)+ RPAREN | ruleName (OR ruleName)+) |
   (DOT | ruleName | LPAREN ruleName (OR ruleName)+ RPAREN) (STAR QUESTION? | QUESTION)) #ruleExpr |
  tokenName STAR? QUESTION? #tokenExpr |
  attributeRef QUESTION? #refExpr;

//keywords & word rules

VISITOR: 'visitor';
FOR: 'for';
GRAMMAR: 'grammar';

lcName: LC_NAME | VISITOR | FOR | GRAMMAR;
ucName: UC_NAME;

identifier: lcName | ucName;
ruleName: lcName;
tokenName: ucName;
attributeRef: ATTRIBUTE_REF;

//other tokens

COMMA: ',';
DOT: '.';
COLON: ':';
STAR: '*';
QUESTION: '?';
SEMI: ';';
EQUALS: '=';
OR: '|';
LPAREN: '(';
RPAREN: ')';
LBRACKET: '[';
RBRACKET: ']';
LBRACE: '{';
RBRACE: '}';

LC_NAME: [a-z][_a-zA-Z0-9]*;
UC_NAME: [A-Z][_a-zA-Z0-9]*;
ATTRIBUTE_REF: '`' [a-zA-Z][_a-zA-Z0-9]* '`';
NUMBER: [0-9]+;

COMMENT: '//' ~[\r\n\f]* -> channel(HIDDEN);
WS: [ \t\r\n\f]+ -> channel(HIDDEN);
