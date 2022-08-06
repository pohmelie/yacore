from types import MappingProxyType

from yacore.log.stdlib import deep_merge


def case(expected, target, *args):
    result = deep_merge(target, *args)
    assert result == expected
    return result


def test_simple():
    case({}, {})
    case({}, {}, {})
    case({}, {}, {}, {})
    case(2, 1, 2)
    case(2, {}, 2)
    case({}, 1, {})
    case(2, [], 2)
    case([], 1, [])
    case({}, [], {})
    case([], {}, [])
    case(2, set(), 2)
    case(set(), 1, set())


def test_strings():
    case("foo", "bar", "foo")
    case("foo", {}, "foo")
    case({}, "bar", {})
    case("foo", [], "foo")
    case([], "bar", [])


def test_bytes():
    case(b"foo", b"bar", b"foo")
    case(b"foo", {}, b"foo")
    case({}, b"bar", {})
    case(b"foo", [], b"foo")
    case([], b"bar", [])


def test_lists():
    case([1], [], [1])
    case([1], [1], [])
    case([1, 2], [1], [2])


def test_tuples():
    case((1,), (), (1,))
    case((1,), (1,), ())
    case((1, 2), (1,), (2,))


def test_dicts():
    case({1: 2}, {}, {1: 2})
    case({1: 2}, {1: 2}, {})
    case({1: 3}, {1: 2}, {1: 3})
    case({1: 4}, {1: 2}, {1: 3}, {1: 4})


def test_frozen_dicts():
    def _f(d):
        return MappingProxyType(d)

    case(_f({1: 2}), _f({}), _f({1: 2}))
    case(_f({1: 2}), _f({1: 2}), _f({}))
    case(_f({1: 3}), _f({1: 2}), _f({1: 3}))
    case(_f({1: 4}), _f({1: 2}), _f({1: 3}), _f({1: 4}))


def test_sets():
    case({1}, set(), {1})
    case({1}, {1}, set())
    case({1, 2}, {1}, {2})
    case({1}, {1}, {1})


def test_frozen_sets():
    def _f(s=()):
        return frozenset(s)

    case(_f({1}), _f(), _f({1}))
    case(_f({1}), _f({1}), _f())
    case(_f({1, 2}), _f({1}), _f({2}))
    case(_f({1}), _f({1}), _f({1}))


def test_nested():
    case({1: [2, 3]}, {1: [2]}, {1: [3]})
    case({1: {2, 3, 4}}, {1: {2, 3}}, {1: {2, 4}})
    case({1: {2: 3, 5: 6}}, {1: {2: 3}}, {1: {5: 6}})
    case({1: {2: (3, 4)}}, {1: {2: (3,)}}, {1: {2: (4,)}})


def test_none():
    case(1, 1, None)
    case(1, None, 1)
    case({1: 2}, {1: 2}, None)
    case({1: 2}, None, {1: 2})


def test_mutation_dict():
    x = {1: 2}
    result = case({1: 2}, None, x)
    case({1: 2, 3: 4}, result, {3: 4})
    assert x == {1: 2}


def test_mutation_seq():
    x = [1]
    result = case([1], None, x)
    case([1, 2], result, [2])
    assert x == [1]


def test_mutation_set():
    x = {1, 2}
    result = case({1, 2}, None, x)
    case({1, 2, 3}, result, {2, 3})
    assert x == {1, 2}
