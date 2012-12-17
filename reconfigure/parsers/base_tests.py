class BaseParserTest (object):
    source = ""
    parsed = None
    parser = None

    def test_parse(self):
        if not self.__class__.parser:
            return

        nodetree = self.parser.parse(self.__class__.source)
        self.assertEquals(self.__class__.parsed, nodetree)

    def test_stringify(self):
        if not self.__class__.parser:
            return

        unparsed = self.parser.stringify(self.__class__.parsed)
        a, b = self.__class__.source, unparsed
        if a.split() != b.split():
            print 'SOURCE: %s\n\nGENERATED: %s' % (a, b)
            self.assertEquals(a.split(), b.split())