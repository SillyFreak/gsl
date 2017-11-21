grammar HedgehogTest;

expr: message* EOF;

message:
  messageType=qualifiedIdentifier discriminator=identifier EQUALS label=number LBRACE
    DOCSTRING?

    (field | oneof)*
    messageClass*
  RBRACE;

field:
  rep='repeated'? fieldType=identifier name=identifier EQUALS label=number LBRACE
    languageFieldSpec*
  RBRACE;

oneof:
  'oneof' name=identifier LBRACE
    field*
  RBRACE;

languageFieldSpec:
  'Python' COLON STRING (COMMA STRING)? SEMI #pythonSpec |
  'TypeScript' COLON STRING (COMMA STRING)? SEMI #typeScriptSpec;

messageClass:
  (REQ | REP | UPD) qualifiedIdentifier LPAREN paramList RPAREN
    DOCSTRING? SEMI;

paramList:
  mandatoryParamList (COMMA repeatedParam)? (COMMA optionalParamList)? |
  repeatedParam (COMMA optionalParamList)? |
  optionalParamList |
  ;

mandatoryParamList: identifier (COMMA identifier)*;
repeatedParam: STAR identifier;
optionalParamList: LBRACKET optionalParam (COMMA optionalParam)* RBRACKET;
optionalParam: identifier (SLASH identifier)*;

qualifiedIdentifier: identifier (DOT identifier)*;
identifier: IDENTIFIER;
number: NUMBER;

DOCSTRING: '"""' (~'\\' | '\\' .)*? '"""';
STRING: '"' (~'\\' | '\\' .)*? '"';
DOT: '.';
COMMA: ',';
COLON: ':';
SEMI: ';';
SLASH: '/';
EQUALS: '=';
STAR: '*';
REQ: '=>';
REP: '<=';
UPD: '<-';
LPAREN: '(';
RPAREN: ')';
LBRACKET: '[';
RBRACKET: ']';
LBRACE: '{';
RBRACE: '}';
IDENTIFIER: [_a-zA-Z][_a-zA-Z0-9]*;
NUMBER: [0-9]+;

COMMENT: '//' ~[\r\n\f]* -> channel(HIDDEN);
WS: [ \t\r\n\f]+ -> channel(HIDDEN);
