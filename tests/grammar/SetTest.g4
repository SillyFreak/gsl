grammar SetTest;

expr: set0 EOF;
set0: LBRACE (element (COMMA element)*)? RBRACE;
element: simpleElement | set0;
simpleElement: NUMBER #IntElement;

COMMA: ',';
LBRACE: '{';
RBRACE: '}';
NUMBER: [0-9]+;

WS: [ \t]+ -> channel(HIDDEN);
