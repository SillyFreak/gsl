grammar GSL;

gsl:
  NEWLINE? line
  (NEWLINE line)*
  EOF;

line:
  CODE #code |
  TEMPLATE #template |
  FTEMPLATE #fTemplate |
  STRING #string |
  FSTRING #fString |
  #emptyLine ;

fragment MARKER: '>';
fragment FMARKER: '`';
fragment QUOT: '"""';
fragment CONTENT: ~[\r\n\f]+;

fragment SPACES: [ \t]+;
fragment EOL: '\r'? '\n' | '\r' | '\f';
NEWLINE:
   { self.line == 1 and self.column == 0 }? SPACES |
   EOL SPACES?;

TEMPLATE: MARKER CONTENT;
FTEMPLATE: FMARKER CONTENT;

STRING: MARKER QUOT EOL .*? EOL SPACES? MARKER QUOT;
FSTRING: FMARKER QUOT EOL .*? EOL SPACES? FMARKER QUOT;

CODE: ~[>`\r\n\f] CONTENT?;
