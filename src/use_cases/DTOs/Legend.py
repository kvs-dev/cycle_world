import zope.interface

class Legend(zope.interface.Interface):
    title = zope.interface.Attribute("Title of the legend")
    loc = zope.interface.Attribute("Location of the legend")

@zope.interface.implementer(Legend)
class LegendImplementation:
    def __init__(self, title: str, loc: str):
        self.title = title
        self.loc = loc