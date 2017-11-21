grammar ExprTest;

expr: expr0 EOF;
expr0: summand ((ADD | SUB) summand)*;
summand: factor ((MUL | DIV) factor)*;
factor:
  NUMBER #number |
  LPAR expr0 RPAR #subexpr;

ADD: '+';
SUB: '-';
MUL: '*';
DIV: '/';
LPAR: '(';
RPAR: ')';
NUMBER: [0-9];

WS: [ \t]+ -> channel(HIDDEN);
