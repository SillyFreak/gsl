grammar SimpleClass;

model: classDef* EOF;

classDef: 'class' IDENTIFIER '{' (fieldDef | methodDef)* '}';
fieldDef: 'field' IDENTIFIER ';';
methodDef: 'method' IDENTIFIER ';';

IDENTIFIER: [_a-zA-Z][a-zA-Z0-9]*;

WS: [ \t]+ -> channel(HIDDEN);
