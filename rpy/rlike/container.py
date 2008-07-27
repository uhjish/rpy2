import itertools

class ArgsDict(dict):
    """ Implements the Ordered Dict API defined in PEP 372.
    When `odict` becomes part of collections, this class 
    should inherit from it rather than from `dict`.

    This class differs a little from the Ordered Dict
    proposed in PEP 372 by the fact that:

    - not all elements have to be named. None has key value means
    an absence of name for the element.

    - unlike in R, all names are unique.

    """

    def __init__(self, c=[]):

        if isinstance(c, TaggedList):
            c = c.items()

        if isinstance(c, dict):
            #FIXME: allow instance from ArgsDict ?
            raise ValueError('A regular dictionnary does not ' +\
                                 'conserve the order of its keys.')

        super(ArgsDict, self).__init__()
        self.__l = []
        l = self.__l

        for k,v in c:
            self[k] = v


    def __cmp__(self, o):
        raise(Exception("Not yet implemented."))

    def __eq__(self):
        raise(Exception("Not yet implemented."))
        
    def __getitem__(self, key):
        if key is None:
            raise ValueError("Unnamed items cannot be retrieved by key.")
        i = super(ArgsDict, self).__getitem__(key)
        return self.__l[i][1]

    def __iter__(self):
        l = self.__l
        for e in l:
            k = e[0]
            if k is None:
                continue
            else:
                yield k

    def __len__(self):
        return len(self.__l)

    def __ne__(self):
        raise(Exception("Not yet implemented."))

    def __repr__(self):
        s = 'o{'
        for k,v in self.iteritems():
            s += "'" + str(k) + "': " + str(v) + ", "
        s += '}'
        return s

    def __reversed__(self):
        raise(Exception("Not yet implemented."))

    def __setitem__(self, key, value):
        """ Replace the element if the key is known, 
        and conserve its rank in the list, or append
        it if unknown. """

        if key is None:
            self.__l.append((key, value))
            return

        if self.has_key(key):
            i = self.index(key)
            self.__l[i] = (key, value)
        else:
            self.__l.append((key, value))
            super(ArgsDict, self).__setitem__(key, len(self.__l)-1)
            
    def byindex(self, i):
        """ Fetch a value by index (rank), rather than by key."""
        return self.__l[i]

    def index(self, k):
        """ Return the index (rank) for the key 'k' """
        return super(ArgsDict, self).__getitem__(k)

    def items(self):
        """ Return an ordered list of all key/value pairs """
        res = [self.byindex(i) for i in xrange(len(self.__l))]
        return tuple(res)

    def iteritems(self):
        return iter(self.__l)

    def reverse(self):
        """ Reverse the order of the elements in-place (no copy)."""
        l = self.__l
        n = len(self.__l)
        for i in xrange(n/2):
            tmp = l[i]
            l[i] = l[n-i-1]
            kv = l[i]
            if kv is not None:
                super(ArgsDict, self).__setitem__(kv[0], i)
            l[n-i-1] = tmp
            kv = tmp
            if kv is not None:
                super(ArgsDict, self).__setitem__(kv[0], n-i-1)
            

    def sort(self, cmp=None, key=None, reverse=False):
        raise(Exception("Not yet implemented."))

    
class TaggedList(list):
    """ A list for which each item has a 'tag'. """

    def __add__(self, tl):
        try:
            tags = tl.tags()
        except AttributeError, ae:
            raise ValueError('Can only concatenate TaggedLists.')
        res = TaggedList(list(self) + list(tl), 
                         tags = self.tags() + tl.tags())
        return res

    def __delitem__(self, y):
        super(TaggedList, self).__delitem__(y)
        self.__tags.__delitem__(y)

    def __delslice__(self, i, j):
        super(TaggedList, self).__delslice__(i, j)
        self.__tags.__delslice__(i, j)

    def __iadd__(self, y):
        super(TaggedList, self).__iadd__(y)
        if isinstance(y, TaggedList):
            self.__tags.__iadd__(y.tags())
        else:
            self.__tags.__iadd__([None, ] * len(y))
        return self

    def __imul__(self, y):
        restags = self.__tags.__imul__(y)
        resitems = super(TaggedList, self).__imul__(y)
        return self

    def __init__(self, l, tags = None):

        super(TaggedList, self).__init__(l)

        if tags is None:
            tags = [None, ] * len(l)
        tags = list(tags)

        if isinstance(tags, list):
            if len(tags) != len(l):
                raise ValueError("When a list, the parameter 'tags' must be of same length as the given list.")
            self.__tags = tags
        else:
            raise ValueError("Parameter 'tags' must be either a list or 'None'.")

    def __setslice__(self, i, j, y):
        #FIXME: implement
        raise Exception("Not yet implemented.")

    def append(self, obj, tag = None):
        super(TaggedList, self).append(obj)
        self.__tags.append(tag)

    def extend(self, iterable):
        if isinstance(iterable, TaggedList):
            itertags = iterable.itertags()
        else:
            itertags = [None, ] * len(iterable)

        for tag, item in itertools.izip(itertags, iterable):
            self.append(item, tag=tag)


    def insert(self, index, obj, tag=None):
        super(TaggedList, self).insert(index, obj)
        self.__tags.insert(index, tag)

    def items(self):
        """ Return a tuple of all pairs (tag, item). """
        res = [(tag, item) for tag, item in itertools.izip(self.__tags, self)]
        return tuple(res)

    def iterontag(self, tag):
        """ iterate on items marked with one given tag. """
        i = 0
        for onetag in self.__tags:
            if tag == onetag:
                yield self[i]
            i += 1

    def itertags(self):
        """ iterate on tags. """
        for tag in self.__tags:
            yield tag

    def pop(self, index=None):
        if index is None:
            index = len(self) - 1
        
        super(TaggedList, self).pop(index)
        self.__tags.pop(index)

    def remove(self, value):
        found = False
        for i in xrange(len(self)):
            if self[i] == value:
                found = True
                break
        if found:
            self.pop(i)

    def reverse(self):
        super(TaggedList, self).reverse()
        self.__tags.reverse()

    def sort(self):
        #FIXME: implement
        raise Exception("Not yet implemented.")

    
    def tags(self):
        """ Return a tuple of all tags """
        res = [x for x in self.__tags]
        return tuple(res)


    def settag(self, i, t):
        """ Set tag 't' for item 'i'. """
        self.__tags[i] = t
