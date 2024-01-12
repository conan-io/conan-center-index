import functools
import struct
import primitives


_typemap = {}


def _cbor_read_intlike(cbor, offset, info):
    """Parses the additional information and reads any additional bytes it
    specifies the existence of, and returns the encoded integer. offset
    should point to the byte immediately following the initial byte. Returns
    the encoded integer and the offset immediately following the object."""

    # Info less than 24 is a shorthand for the integer itself.
    if info < 24:
        return info, offset

    # 24 is 8-bit following the info byte.
    if info == 24:
        return cbor[offset], offset + 1

    # 25 is 16-bit following the info byte.
    if info == 25:
        val, = struct.unpack('>H', cbor[offset:offset+2])
        return val, offset + 2

    # 26 is 32-bit following the info byte.
    if info == 26:
        val, = struct.unpack('>I', cbor[offset:offset+4])
        return val, offset + 4

    # 27 is 64-bit following the info byte.
    if info == 27:
        val, = struct.unpack('>Q', cbor[offset:offset+8])
        return val, offset + 8

    # Info greater than or equal to 28 is illegal. Note that 31 is used for
    # indefinite lengths, so this must be checked prior to calling this
    # method.
    raise ValueError("invalid CBOR: illegal additional info for integer or object length")


def _sub_cbor_to_py(cbor, offset):
    """Converts the CBOR object starting at cbor[offset] to its Python
    representation for as far as tree-gen supports CBOR. Returns this Python
    representation and the offset immediately following the CBOR representation
    thereof. Supported types:

     - 0: unsigned integer (int)
     - 1: negative integer (int)
     - 2: byte string (bytes)
     - 3: UTF-8 string (str)
     - 4: array (list)
     - 5: map (dict)
     - 6: semantic tag (ignored)
     - 7.20: false (bool)
     - 7.21: true (bool)
     - 7.22: null (NoneType)
     - 7.27: double-precision float (float)

    Both definite-length and indefinite-length notation is supported for sized
    objects (strings, arrays, maps). A ValueError is thrown if the CBOR is
    invalid or contains unsupported structures."""

    # Read the initial byte.
    initial = cbor[offset]
    typ = initial >> 5
    info = initial & 0x1F
    offset += 1

    # Handle unsigned integer (0) and negative integer (1).
    if typ <= 1:
        value, offset = _cbor_read_intlike(cbor, offset, info)
        if typ == 1:
            value = -1 - value
        return value, offset

    # Handle byte string (2) and UTF-8 string (3).
    if typ <= 3:

        # Gather components of the string in here.
        if info == 31:

            # Handle indefinite length strings. These consist of a
            # break-terminated (0xFF) list of definite-length strings of the
            # same type.
            value = []
            while True:
                sub_initial = cbor[offset]; offset += 1
                if sub_initial == 0xFF:
                    break
                sub_typ = sub_initial >> 5
                sub_info = sub_initial & 0x1F
                if sub_typ != typ:
                    raise ValueError('invalid CBOR: illegal indefinite-length string component')

                # Seek past definite-length string component. The size in
                # bytes is encoded as an integer.
                size, offset = _cbor_read_intlike(cbor, offset, sub_info)
                value.append(cbor[offset:offset + size])
                offset += size
            value = b''.join(value)

        else:

            # Handle definite-length strings. The size in bytes is encoded as
            # an integer.
            size, offset = _cbor_read_intlike(cbor, offset, info)
            value = cbor[offset:offset + size]
            offset += size

        if typ == 3:
            value = value.decode('UTF-8')
        return value, offset

    # Handle array (4) and map (5).
    if typ <= 5:

        # Create result container.
        container = [] if typ == 4 else {}

        # Handle indefinite length arrays and maps.
        if info == 31:

            # Read objects/object pairs until we encounter a break.
            while cbor[offset] != 0xFF:
                if typ == 4:
                    value, offset = _sub_cbor_to_py(cbor, offset)
                    container.append(value)
                else:
                    key, offset = _sub_cbor_to_py(cbor, offset)
                    if not isinstance(key, str):
                        raise ValueError('invalid CBOR: map key is not a UTF-8 string')
                    value, offset = _sub_cbor_to_py(cbor, offset)
                    container[key] = value

            # Seek past the break.
            offset += 1

        else:

            # Handle definite-length arrays and maps. The amount of
            # objects/object pairs is encoded as an integer.
            size, offset = _cbor_read_intlike(cbor, offset, info)
            for _ in range(size):
                if typ == 4:
                    value, offset = _sub_cbor_to_py(cbor, offset)
                    container.append(value)
                else:
                    key, offset = _sub_cbor_to_py(cbor, offset)
                    if not isinstance(key, str):
                        raise ValueError('invalid CBOR: map key is not a UTF-8 string')
                    value, offset = _sub_cbor_to_py(cbor, offset)
                    container[key] = value

        return container, offset

    # Handle semantic tags.
    if typ == 6:

        # We don't use semantic tags for anything, but ignoring them is
        # legal and reading past them is easy enough.
        _, offset = _cbor_read_intlike(cbor, offset, info)
        return _sub_cbor_to_py(cbor, offset)

    # Handle major type 7. Here, the type is defined by the additional info.
    # Additional info 24 is reserved for having the type specified by the
    # next byte, but all such values are unassigned.
    if info == 20:
        # false
        return False, offset

    if info == 21:
        # true
        return True, offset

    if info == 22:
        # null
        return None, offset

    if info == 23:
        # Undefined value.
        raise ValueError('invalid CBOR: undefined value is not supported')

    if info == 25:
        # Half-precision float.
        raise ValueError('invalid CBOR: half-precision float is not supported')

    if info == 26:
        # Single-precision float.
        raise ValueError('invalid CBOR: single-precision float is not supported')

    if info == 27:
        # Double-precision float.
        value, = struct.unpack('>d', cbor[offset:offset+8])
        return value, offset + 8

    if info == 31:
        # Break value used for indefinite-length objects.
        raise ValueError('invalid CBOR: unexpected break')

    raise ValueError('invalid CBOR: unknown type code')


def _cbor_to_py(cbor):
    """Converts the given CBOR object (bytes) to its Python representation for
    as far as tree-gen supports CBOR. Supported types:

     - 0: unsigned integer (int)
     - 1: negative integer (int)
     - 2: byte string (bytes)
     - 3: UTF-8 string (str)
     - 4: array (list)
     - 5: map (dict)
     - 6: semantic tag (ignored)
     - 7.20: false (bool)
     - 7.21: true (bool)
     - 7.22: null (NoneType)
     - 7.27: double-precision float (float)

    Both definite-length and indefinite-length notation is supported for sized
    objects (strings, arrays, maps). A ValueError is thrown if the CBOR is
    invalid or contains unsupported structures."""

    value, length = _sub_cbor_to_py(cbor, 0)
    if length < len(cbor):
        raise ValueError('invalid CBOR: garbage at the end')
    return value


class _Cbor(bytes):
    """Marker class indicating that this bytes object represents CBOR."""
    pass


def _cbor_write_intlike(value, major=0):
    """Converts the given integer to its minimal representation in CBOR. The
    major code can be overridden to write lengths for strings, arrays, and
    maps."""

    # Negative integers use major code 1.
    if value < 0:
        major = 1
        value = -1 - value
    initial = major << 5

    # Use the minimal representation.
    if value < 24:
        return struct.pack('>B', initial | value)
    if value < 0x100:
        return struct.pack('>BB', initial | 24, value)
    if value < 0x10000:
        return struct.pack('>BH', initial | 25, value)
    if value < 0x100000000:
        return struct.pack('>BI', initial | 26, value)
    if value < 0x10000000000000000:
        return struct.pack('>BQ', initial | 27, value)

    raise ValueError('integer too large for CBOR (bigint not supported)')


def _py_to_cbor(value, type_converter=None):
    """Inverse of _cbor_to_py(). type_converter optionally specifies a function
    that takes a value and either converts it to a primitive for serialization,
    converts it to a _Cbor object manually, or raises a TypeError if no
    conversion is known. If no type_converter is specified, a TypeError is
    raised in all cases the type_converter would otherwise be called. The cbor
    serialization is returned using a _Cbor object, which is just a marker class
    behaving just like bytes."""
    if isinstance(value, _Cbor):
        return value

    if isinstance(value, int):
        return _Cbor(_cbor_write_intlike(value))

    if isinstance(value, float):
        return _Cbor(struct.pack('>Bd', 0xFB, value))

    if isinstance(value, str):
        value = value.encode('UTF-8')
        return _Cbor(_cbor_write_intlike(len(value), 3) + value)

    if isinstance(value, bytes):
        return _Cbor(_cbor_write_intlike(len(value), 2) + value)

    if value is False:
        return _Cbor(b'\xF4')

    if value is True:
        return _Cbor(b'\xF5')

    if value is None:
        return _Cbor(b'\xF6')

    if isinstance(value, (list, tuple)):
        cbor = [_cbor_write_intlike(len(value), 4)]
        for val in value:
            cbor.append(_py_to_cbor(val, type_converter))
        return _Cbor(b''.join(cbor))

    if isinstance(value, dict):
        cbor = [_cbor_write_intlike(len(value), 5)]
        for key, val in sorted(value.items()):
            if not isinstance(key, str):
                raise TypeError('dict keys must be strings')
            cbor.append(_py_to_cbor(key, type_converter))
            cbor.append(_py_to_cbor(val, type_converter))
        return _Cbor(b''.join(cbor))

    if type_converter is not None:
        return _py_to_cbor(type_converter(value))

    raise TypeError('unsupported type for conversion to cbor: %r' % (value,))


class NotWellFormed(ValueError):
    """Exception class for well-formedness checks."""

    def __init__(self, msg):
        super().__init__('not well-formed: ' + str(msg))


class Node(object):
    """Base class for nodes."""

    __slots__ = ['_annot']

    def __init__(self):
        super().__init__()
        self._annot = {}

    def __getitem__(self, key):
        """Returns the annotation object with the specified key, or raises
        KeyError if not found."""
        if not isinstance(key, str):
            raise TypeError('indexing a node with something other than an '
                            'annotation key string')
        return self._annot[key]

    def __setitem__(self, key, val):
        """Assigns the annotation object with the specified key."""
        if not isinstance(key, str):
            raise TypeError('indexing a node with something other than an '
                            'annotation key string')
        self._annot[key] = val

    def __delitem__(self, key):
        """Deletes the annotation object with the specified key."""
        if not isinstance(key, str):
            raise TypeError('indexing a node with something other than an '
                            'annotation key string')
        del self._annot[key]

    def __contains__(self, key):
        """Returns whether an annotation exists for the specified key."""
        return key in self._annot

    @staticmethod
    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it. Note that this is overridden
        by the actual node class implementations; this base function does very
        little."""
        if id_map is None:
            id_map = {}
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes. Note that this is
        overridden by the actual node class implementations; this base function
        always raises an exception."""
        raise NotWellFormed('found node of abstract type ' + type(self).__name__)

    def check_well_formed(self):
        """Checks whether the tree starting at this node is well-formed. That
        is:

         - all One, Link, and Many edges have (at least) one entry;
         - all the One entries internally stored by Any/Many have an entry;
         - all Link and filled OptLink nodes link to a node that's reachable
           from this node;
         - the nodes referred to be One/Maybe only appear once in the tree
           (except through links).

        If it isn't well-formed, a NotWellFormed is thrown."""
        self.check_complete()

    def is_well_formed(self):
        """Returns whether the tree starting at this node is well-formed. That
        is:

         - all One, Link, and Many edges have (at least) one entry;
         - all the One entries internally stored by Any/Many have an entry;
         - all Link and filled OptLink nodes link to a node that's reachable
           from this node;
         - the nodes referred to be One/Maybe only appear once in the tree
           (except through links)."""
        try:
            self.check_well_formed()
            return True
        except NotWellFormed:
            return False

    def copy(self):
        """Returns a shallow copy of this node. Note that this is overridden by
        the actual node class implementations; this base function always raises
        an exception."""
        raise TypeError('can\'t copy node of abstract type ' + type(self).__name__)

    def clone(self):
        """Returns a deep copy of this node. Note that this is overridden by
        the actual node class implementations; this base function always raises
        an exception."""
        raise TypeError('can\'t clone node of abstract type ' + type(self).__name__)

    @classmethod
    def deserialize(cls, cbor):
        """Attempts to deserialize the given cbor object (either as bytes or as
        its Python primitive representation) into a node of this type."""
        if isinstance(cbor, bytes):
            cbor = _cbor_to_py(cbor)
        seq_to_ob = {}
        links = []
        root = cls._deserialize(cbor, seq_to_ob, links)
        for link_setter, seq in links:
            ob = seq_to_ob.get(seq, None)
            if ob is None:
                raise ValueError('found link to nonexistent object')
            link_setter(ob)
        return root

    def serialize(self):
        """Serializes this node into its cbor representation in the form of a
        bytes object."""
        id_map = self.find_reachable()
        self.check_complete(id_map)
        return _py_to_cbor(self._serialize(id_map))

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        node_type = _typemap.get(cbor.get('@t'), None)
        if node_type is None:
            raise ValueError('unknown node type (@t): ' + str(cbor.get('@t')))
        return node_type._deserialize(cbor, seq_to_ob, links)


@functools.total_ordering
class _Multiple(object):
    """Base class for the Any* and Many* edge helper classes. Inheriting
    classes must set the class constant _T to the node type they are made
    for."""

    __slots__ = ['_l']

    def __init__(self,  *args, **kwargs):
        super().__init__()
        self._l = list(*args, **kwargs)
        for idx, val in enumerate(self._l):
            if not isinstance(val, self._T):
                raise TypeError(
                    'object {!r} at index {:d} is not an instance of {!r}'
                    .format(val, idx, self._T))

    def __repr__(self):
        return '{}({!r})'.format(type(self).__name__, self._l)

    def clone(self):
        return self.__class__(map(lambda node: node.clone(), self._l))

    def __len__(self):
        return len(self._l)

    def __getitem__(self, idx):
        return self._l[idx]

    def __setitem__(self, idx, val):
        if not isinstance(val, self._T):
            raise TypeError(
                'object {!r} is not an instance of {!r}'
                .format(val, idx, self._T))
        self._l[idx] = val

    def __delitem__(self, idx):
        del self._l[idx]

    def __iter__(self):
        return iter(self._l)

    def __reversed__(self):
        return reversed(self._l)

    def __contains__(self, val):
        return val in self._l

    def append(self, val):
        if not isinstance(val, self._T):
            raise TypeError(
                'object {!r} is not an instance of {!r}'
                .format(val, self._T))
        self._l.append(val)

    def extend(self, iterable):
        for val in iterable:
            self.append(val)

    def insert(self, idx, val):
        if not isinstance(val, self._T):
            raise TypeError(
                'object {!r} is not an instance of {!r}'
                .format(val, self._T))
        self._l.insert(idx, val)

    def remote(self, val):
        self._l.remove(val)

    def pop(self, idx=-1):
        return self._l.pop(idx)

    def clear(self):
        self._l.clear()

    def idx(self, val, start=0, end=-1):
        return self._l.idx(val, start, end)

    def count(self, val):
        return self._l.count(val)

    def sort(self, key=None, reverse=False):
        self._l.sort(key=key, reverse=reverse)

    def reverse(self):
        self._l.reverse()

    def copy(self):
        return self.__class__(self)

    def __eq__(self, other):
        if not isinstance(other, _Multiple):
            return False
        return self._l == other._l

    def __lt__(self, other):
        return self._l < other._l

    def __iadd__(self, other):
        self.extend(other)

    def __add__(self, other):
        copy = self.copy()
        copy += other
        return copy

    def __imul__(self, other):
        self._l *= other

    def __mul__(self, other):
        copy = self.copy()
        copy *= other
        return copy

    def __rmul__(self, other):
        copy = self.copy()
        copy *= other
        return copy


class MultiNode(_Multiple):
    """Wrapper for an edge with multiple Node objects."""

    _T = Node


def _cloned(obj):
    """Attempts to clone the given object by calling its clone() method, if it
    has one."""
    if hasattr(obj, 'clone'):
        return obj.clone()
    return obj


class Entry(Node):
    """Represents a directory entry."""

    __slots__ = [
        '_attr_name',
    ]

    def __init__(
        self,
        name=None,
    ):
        super().__init__()
        self.name = name

    @property
    def name(self):
        """Name of the directory entry."""
        return self._attr_name

    @name.setter
    def name(self, val):
        if val is None:
            del self.name
            return
        if not isinstance(val, primitives.String):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('name must be of type primitives.String')
            val = primitives.String(val)
        self._attr_name = val

    @name.deleter
    def name(self):
        self._attr_name = primitives.String()

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ == 'File':
            return File._deserialize(cbor, seq_to_ob, links)
        if typ == 'Directory':
            return Directory._deserialize(cbor, seq_to_ob, links)
        if typ == 'Mount':
            return Mount._deserialize(cbor, seq_to_ob, links)
        raise ValueError('unknown or unexpected type (@t) found in node serialization')

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Entry'}

        # Serialize the name field.
        if hasattr(self._attr_name, 'serialize_cbor'):
            cbor['name'] = self._attr_name.serialize_cbor()
        else:
            cbor['name'] = primitives.serialize(primitives.String, self._attr_name)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(primitives.serialize(key, val))

        return cbor


class MultiEntry(_Multiple):
    """Wrapper for an edge with multiple Entry objects."""

    _T = Entry


_typemap['Entry'] = Entry

class Directory(Entry):
    """Represents a (sub)directory."""

    __slots__ = [
        '_attr_entries',
    ]

    def __init__(
        self,
        entries=None,
        name=None,
    ):
        super().__init__(name=name)
        self.entries = entries

    @property
    def entries(self):
        """The directory contents. Note that directories can be empty."""
        return self._attr_entries

    @entries.setter
    def entries(self, val):
        if val is None:
            del self.entries
            return
        if not isinstance(val, MultiEntry):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('entries must be of type MultiEntry')
            val = MultiEntry(val)
        self._attr_entries = val

    @entries.deleter
    def entries(self):
        self._attr_entries = MultiEntry()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Directory):
            return False
        if self.entries != other.entries:
            return False
        if self.name != other.name:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Directory(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('entries: ')
        if not self.entries:
            s.append('-\n')
        else:
            s.append('[\n')
            for child in self.entries:
                s.append(child.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + ']\n')
        s.append('  '*indent)
        s.append('name: ')
        s.append(str(self.name) + '\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        for el in self._attr_entries:
            el.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        for child in self._attr_entries:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Directory(
            entries=self._attr_entries.copy(),
            name=self._attr_name
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Directory(
            entries=_cloned(self._attr_entries),
            name=_cloned(self._attr_name)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'Directory':
            raise ValueError('found node serialization for ' + typ + ', but expected Directory')

        # Deserialize the entries field.
        field = cbor.get('entries', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field entries')
        if field.get('@T') != '*':
            raise ValueError('unexpected edge type for field entries')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_entries = MultiEntry()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_entries.append(Entry._deserialize(element, seq_to_ob, links))

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if hasattr(primitives.String, 'deserialize_cbor'):
            f_name = primitives.String.deserialize_cbor(field)
        else:
            f_name = primitives.deserialize(primitives.String, field)

        # Construct the Directory node.
        node = Directory(f_entries, f_name)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Directory'}

        # Serialize the entries field.
        field = {'@T': '*'}
        lst = []
        for el in self._attr_entries:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['entries'] = field

        # Serialize the name field.
        if hasattr(self._attr_name, 'serialize_cbor'):
            cbor['name'] = self._attr_name.serialize_cbor()
        else:
            cbor['name'] = primitives.serialize(primitives.String, self._attr_name)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(primitives.serialize(key, val))

        return cbor


class MultiDirectory(_Multiple):
    """Wrapper for an edge with multiple Directory objects."""

    _T = Directory


_typemap['Directory'] = Directory

class Drive(Node):
    """Represents a drive."""

    __slots__ = [
        '_attr_letter',
        '_attr_root_dir',
    ]

    def __init__(
        self,
        letter=None,
        root_dir=None,
    ):
        super().__init__()
        self.letter = letter
        self.root_dir = root_dir

    @property
    def letter(self):
        """The drive letter used to identify it."""
        return self._attr_letter

    @letter.setter
    def letter(self, val):
        if val is None:
            del self.letter
            return
        if not isinstance(val, primitives.Letter):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('letter must be of type primitives.Letter')
            val = primitives.Letter(val)
        self._attr_letter = val

    @letter.deleter
    def letter(self):
        self._attr_letter = primitives.Letter()

    @property
    def root_dir(self):
        """Root directory."""
        return self._attr_root_dir

    @root_dir.setter
    def root_dir(self, val):
        if val is None:
            del self.root_dir
            return
        if not isinstance(val, Directory):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('root_dir must be of type Directory')
            val = Directory(val)
        self._attr_root_dir = val

    @root_dir.deleter
    def root_dir(self):
        self._attr_root_dir = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Drive):
            return False
        if self.letter != other.letter:
            return False
        if self.root_dir != other.root_dir:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Drive(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('letter: ')
        s.append(str(self.letter) + '\n')
        s.append('  '*indent)
        s.append('root_dir: ')
        if self.root_dir is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            s.append(self.root_dir.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + '>\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        if self._attr_root_dir is not None:
            self._attr_root_dir.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_root_dir is None:
            raise NotWellFormed('root_dir is required but not set')
        if self._attr_root_dir is not None:
            self._attr_root_dir.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return Drive(
            letter=self._attr_letter,
            root_dir=self._attr_root_dir
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Drive(
            letter=_cloned(self._attr_letter),
            root_dir=_cloned(self._attr_root_dir)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'Drive':
            raise ValueError('found node serialization for ' + typ + ', but expected Drive')

        # Deserialize the letter field.
        field = cbor.get('letter', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field letter')
        if hasattr(primitives.Letter, 'deserialize_cbor'):
            f_letter = primitives.Letter.deserialize_cbor(field)
        else:
            f_letter = primitives.deserialize(primitives.Letter, field)

        # Deserialize the root_dir field.
        field = cbor.get('root_dir', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field root_dir')
        if field.get('@T') != '1':
            raise ValueError('unexpected edge type for field root_dir')
        if field.get('@t', None) is None:
            f_root_dir = None
        else:
            f_root_dir = Directory._deserialize(field, seq_to_ob, links)

        # Construct the Drive node.
        node = Drive(f_letter, f_root_dir)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Drive'}

        # Serialize the letter field.
        if hasattr(self._attr_letter, 'serialize_cbor'):
            cbor['letter'] = self._attr_letter.serialize_cbor()
        else:
            cbor['letter'] = primitives.serialize(primitives.Letter, self._attr_letter)

        # Serialize the root_dir field.
        field = {'@T': '1'}
        if self._attr_root_dir is None:
            field['@t'] = None
        else:
            field.update(self._attr_root_dir._serialize(id_map))
        cbor['root_dir'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(primitives.serialize(key, val))

        return cbor


class MultiDrive(_Multiple):
    """Wrapper for an edge with multiple Drive objects."""

    _T = Drive


_typemap['Drive'] = Drive

class File(Entry):
    """Represents a regular file."""

    __slots__ = [
        '_attr_contents',
    ]

    def __init__(
        self,
        contents=None,
        name=None,
    ):
        super().__init__(name=name)
        self.contents = contents

    @property
    def contents(self):
        """The file contents."""
        return self._attr_contents

    @contents.setter
    def contents(self, val):
        if val is None:
            del self.contents
            return
        if not isinstance(val, primitives.String):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('contents must be of type primitives.String')
            val = primitives.String(val)
        self._attr_contents = val

    @contents.deleter
    def contents(self):
        self._attr_contents = primitives.String()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, File):
            return False
        if self.contents != other.contents:
            return False
        if self.name != other.name:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('File(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('contents: ')
        s.append(str(self.contents) + '\n')
        s.append('  '*indent)
        s.append('name: ')
        s.append(str(self.name) + '\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()

    def copy(self):
        """Returns a shallow copy of this node."""
        return File(
            contents=self._attr_contents,
            name=self._attr_name
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return File(
            contents=_cloned(self._attr_contents),
            name=_cloned(self._attr_name)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'File':
            raise ValueError('found node serialization for ' + typ + ', but expected File')

        # Deserialize the contents field.
        field = cbor.get('contents', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field contents')
        if hasattr(primitives.String, 'deserialize_cbor'):
            f_contents = primitives.String.deserialize_cbor(field)
        else:
            f_contents = primitives.deserialize(primitives.String, field)

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if hasattr(primitives.String, 'deserialize_cbor'):
            f_name = primitives.String.deserialize_cbor(field)
        else:
            f_name = primitives.deserialize(primitives.String, field)

        # Construct the File node.
        node = File(f_contents, f_name)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'File'}

        # Serialize the contents field.
        if hasattr(self._attr_contents, 'serialize_cbor'):
            cbor['contents'] = self._attr_contents.serialize_cbor()
        else:
            cbor['contents'] = primitives.serialize(primitives.String, self._attr_contents)

        # Serialize the name field.
        if hasattr(self._attr_name, 'serialize_cbor'):
            cbor['name'] = self._attr_name.serialize_cbor()
        else:
            cbor['name'] = primitives.serialize(primitives.String, self._attr_name)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(primitives.serialize(key, val))

        return cbor


class MultiFile(_Multiple):
    """Wrapper for an edge with multiple File objects."""

    _T = File


_typemap['File'] = File

class Mount(Entry):
    """Represents a link to another directory."""

    __slots__ = [
        '_attr_target',
    ]

    def __init__(
        self,
        target=None,
        name=None,
    ):
        super().__init__(name=name)
        self.target = target

    @property
    def target(self):
        """The directory linked to."""
        return self._attr_target

    @target.setter
    def target(self, val):
        if val is None:
            del self.target
            return
        if not isinstance(val, Directory):
            raise TypeError('target must be of type Directory')
        self._attr_target = val

    @target.deleter
    def target(self):
        self._attr_target = None

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, Mount):
            return False
        if self.target is not other.target:
            return False
        if self.name != other.name:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('Mount(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('target --> ')
        if self.target is None:
            s.append('!MISSING\n')
        else:
            s.append('<\n')
            if links:
                s.append(self.target.dump(indent + 1, annotations, links - 1) + '\n')
            else:
                s.append('  '*(indent+1) + '...\n')
            s.append('  '*indent + '>\n')
        s.append('  '*indent)
        s.append('name: ')
        s.append(str(self.name) + '\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if self._attr_target is None:
            raise NotWellFormed('target is required but not set')
        if self._attr_target is not None:
            if id(self._attr_target) not in id_map:
                raise NotWellFormed('target links to unreachable node')

    def copy(self):
        """Returns a shallow copy of this node."""
        return Mount(
            target=self._attr_target,
            name=self._attr_name
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return Mount(
            target=self._attr_target,
            name=_cloned(self._attr_name)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'Mount':
            raise ValueError('found node serialization for ' + typ + ', but expected Mount')

        # Deserialize the target field.
        field = cbor.get('target', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field target')
        if field.get('@T') != '$':
            raise ValueError('unexpected edge type for field target')
        f_target = None
        l_target = field.get('@l', None)

        # Deserialize the name field.
        field = cbor.get('name', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field name')
        if hasattr(primitives.String, 'deserialize_cbor'):
            f_name = primitives.String.deserialize_cbor(field)
        else:
            f_name = primitives.deserialize(primitives.String, field)

        # Construct the Mount node.
        node = Mount(f_target, f_name)

        # Register links to be made after tree construction.
        links.append((lambda val: Mount.target.fset(node, val), l_target))

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'Mount'}

        # Serialize the target field.
        field = {'@T': '$'}
        if self._attr_target is None:
            field['@l'] = None
        else:
            field['@l'] = id_map[id(self._attr_target)]
        cbor['target'] = field

        # Serialize the name field.
        if hasattr(self._attr_name, 'serialize_cbor'):
            cbor['name'] = self._attr_name.serialize_cbor()
        else:
            cbor['name'] = primitives.serialize(primitives.String, self._attr_name)

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(primitives.serialize(key, val))

        return cbor


class MultiMount(_Multiple):
    """Wrapper for an edge with multiple Mount objects."""

    _T = Mount


_typemap['Mount'] = Mount

class System(Node):
    """Root node, containing the drives and associated directory trees."""

    __slots__ = [
        '_attr_drives',
    ]

    def __init__(
        self,
        drives=None,
    ):
        super().__init__()
        self.drives = drives

    @property
    def drives(self):
        """The drives available on the system. There must be at least one."""
        return self._attr_drives

    @drives.setter
    def drives(self, val):
        if val is None:
            del self.drives
            return
        if not isinstance(val, MultiDrive):
            # Try to "typecast" if this isn't an obvious mistake.
            if isinstance(val, Node):
                raise TypeError('drives must be of type MultiDrive')
            val = MultiDrive(val)
        self._attr_drives = val

    @drives.deleter
    def drives(self):
        self._attr_drives = MultiDrive()

    def __eq__(self, other):
        """Equality operator. Ignores annotations!"""
        if not isinstance(other, System):
            return False
        if self.drives != other.drives:
            return False
        return True

    def dump(self, indent=0, annotations=None, links=1):
        """Returns a debug representation of this tree as a multiline string.
        indent is the number of double spaces prefixed before every line.
        annotations, if specified, must be a set-like object containing the key
        strings of the annotations that are to be printed. links specifies the
        maximum link recursion depth."""
        s = ['  '*indent]
        s.append('System(')
        if annotations is None:
            annotations = []
        for key in annotations:
            if key in self:
                s.append(' # {}: {}'.format(key, self[key]))
        s.append('\n')
        indent += 1
        s.append('  '*indent)
        s.append('drives: ')
        if not self.drives:
            s.append('!MISSING\n')
        else:
            s.append('[\n')
            for child in self.drives:
                s.append(child.dump(indent + 1, annotations, links) + '\n')
            s.append('  '*indent + ']\n')
        indent -= 1
        s.append('  '*indent)
        s.append(')')
        return ''.join(s)

    __str__ = dump
    __repr__ = dump

    def find_reachable(self, id_map=None):
        """Returns a dictionary mapping Python id() values to stable sequence
        numbers for all nodes in the tree rooted at this node. If id_map is
        specified, found nodes are appended to it."""
        if id_map is None:
            id_map = {}
        if id(self) in id_map:
            raise NotWellFormed('node {!r} with id {} occurs more than once'.format(self, id(self)))
        id_map[id(self)] = len(id_map)
        for el in self._attr_drives:
            el.find_reachable(id_map)
        return id_map

    def check_complete(self, id_map=None):
        """Raises NotWellFormed if the tree rooted at this node is not
        well-formed. If id_map is specified, this tree is only a subtree in the
        context of a larger tree, and id_map must be a dict mapping from Python
        id() codes to tree indices for all reachable nodes."""
        if id_map is None:
            id_map = self.find_reachable()
        if not self._attr_drives:
            raise NotWellFormed('drives needs at least one node but has zero')
        for child in self._attr_drives:
            child.check_complete(id_map)

    def copy(self):
        """Returns a shallow copy of this node."""
        return System(
            drives=self._attr_drives.copy()
        )

    def clone(self):
        """Returns a deep copy of this node. This mimics the C++ interface,
        deficiencies with links included; that is, links always point to the
        original tree. If you're not cloning a subtree in a context where this
        is the desired behavior, you may want to use the copy.deepcopy() from
        the stdlib instead, which should copy links correctly."""
        return System(
            drives=_cloned(self._attr_drives)
        )

    @staticmethod
    def _deserialize(cbor, seq_to_ob, links):
        """Attempts to deserialize the given cbor object (in Python primitive
        representation) into a node of this type. All (sub)nodes are added to
        the seq_to_ob dict, indexed by their cbor sequence number. All links are
        registered in the links list by means of a two-tuple of the setter
        function for the link field and the sequence number of the target node.
        """
        if not isinstance(cbor, dict):
            raise TypeError('node description object must be a dict')
        typ = cbor.get('@t', None)
        if typ is None:
            raise ValueError('type (@t) field is missing from node serialization')
        if typ != 'System':
            raise ValueError('found node serialization for ' + typ + ', but expected System')

        # Deserialize the drives field.
        field = cbor.get('drives', None)
        if not isinstance(field, dict):
            raise ValueError('missing or invalid serialization of field drives')
        if field.get('@T') != '+':
            raise ValueError('unexpected edge type for field drives')
        data = field.get('@d', None)
        if not isinstance(data, list):
            raise ValueError('missing serialization of Any/Many contents')
        f_drives = MultiDrive()
        for element in data:
            if element.get('@T') != '1':
                raise ValueError('unexpected edge type for Any/Many element')
            f_drives.append(Drive._deserialize(element, seq_to_ob, links))

        # Construct the System node.
        node = System(f_drives)

        # Deserialize annotations.
        for key, val in cbor.items():
            if not (key.startswith('{') and key.endswith('}')):
                continue
            key = key[1:-1]
            node[key] = primitives.deserialize(key, val)

        # Register node in sequence number lookup.
        seq = cbor.get('@i', None)
        if not isinstance(seq, int):
            raise ValueError('sequence number field (@i) is not an integer or missing from node serialization')
        if seq in seq_to_ob:
            raise ValueError('duplicate sequence number %d' % seq)
        seq_to_ob[seq] = node

        return node

    def _serialize(self, id_map):
        """Serializes this node to the Python primitive representation of its
        CBOR serialization. The tree that the node belongs to must be
        well-formed. id_map must match Python id() calls for all nodes to unique
        integers, to use for the sequence number representation of links."""
        cbor = {'@i': id_map[id(self)], '@t': 'System'}

        # Serialize the drives field.
        field = {'@T': '+'}
        lst = []
        for el in self._attr_drives:
            el = el._serialize(id_map)
            el['@T'] = '1'
            lst.append(el)
        field['@d'] = lst
        cbor['drives'] = field

        # Serialize annotations.
        for key, val in self._annot.items():
            cbor['{%s}' % key] = _py_to_cbor(primitives.serialize(key, val))

        return cbor


class MultiSystem(_Multiple):
    """Wrapper for an edge with multiple System objects."""

    _T = System


_typemap['System'] = System

