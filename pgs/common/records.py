class Record:
    """Base class upon which specific types may be derived."""
    FIELDS = []

    def __init__(self, initializing_dict=None):
        for fld in self.FIELDS:
            setattr(self, fld, None)
        if initializing_dict:
            self.loaddict(initializing_dict)

    def get_field(self, name):
        """Get the value of a named attribute."""
        return getattr(self, name)

    def set_field(self, name, value):
        """Set named attribute to the given value."""
        setattr(self, name, value)
        return None

    def loaddict(self, datadict):
        """Loads dictionary into attributes named to match its keys."""
        for k,v in datadict.items():
            self.set_field(k, v)

    @property
    def data(self):
        """Return copy, not direct access."""
        return dict(self.__dict__)
