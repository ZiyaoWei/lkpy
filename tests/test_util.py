import time

import numpy as np

from pytest import approx

from lenskit import util as lku
from lenskit import _cy_util as lkcu


def test_stopwatch_instant():
    w = lku.Stopwatch()
    assert w.elapsed() > 0


def test_stopwatch_sleep():
    w = lku.Stopwatch()
    time.sleep(0.5)
    assert w.elapsed() == approx(0.5, abs=0.1)


def test_stopwatch_stop():
    w = lku.Stopwatch()
    time.sleep(0.5)
    w.stop()
    time.sleep(0.5)
    assert w.elapsed() == approx(0.5, abs=0.1)


def test_stopwatch_str():
    w = lku.Stopwatch()
    time.sleep(0.5)
    s = str(w)
    assert s.endswith('ms')


def test_stopwatch_long_str():
    w = lku.Stopwatch()
    time.sleep(1.2)
    s = str(w)
    assert s.endswith('s')


def test_accum_init_empty():
    values = np.empty(0)
    acc = lku.Accumulator(values, 10)

    assert acc is not None
    assert len(acc) == 0
    assert acc.peek() < 0
    assert acc.remove() < 0


def test_accum_add_get():
    values = np.array([1.5])
    acc = lku.Accumulator(values, 10)

    assert acc is not None
    assert len(acc) == 0
    assert acc.peek() < 0
    assert acc.remove() < 0

    acc.add(0)
    assert len(acc) == 1
    assert acc.peek() == 0
    assert acc.remove() == 0
    assert len(acc) == 0
    assert acc.peek() == -1


def test_accum_add_a_few():
    values = np.array([1.5, 2, -1])
    acc = lku.Accumulator(values, 10)

    assert acc is not None
    assert len(acc) == 0

    acc.add(1)
    acc.add(0)
    acc.add(2)

    assert len(acc) == 3
    assert acc.peek() == 2
    assert acc.remove() == 2
    assert len(acc) == 2
    assert acc.remove() == 0
    assert acc.remove() == 1
    assert len(acc) == 0


def test_accum_add_a_few_lim():
    values = np.array([1.5, 2, -1])
    acc = lku.Accumulator(values, 2)

    assert acc is not None
    assert len(acc) == 0

    acc.add(1)
    acc.add(0)
    acc.add(2)

    assert len(acc) == 2
    assert acc.remove() == 0
    assert len(acc) == 1
    assert acc.remove() == 1
    assert len(acc) == 0


def test_accum_add_more_lim():
    for run in range(10):
        values = np.random.randn(100)
        acc = lku.Accumulator(values, 10)

        order = np.arange(len(values), dtype=np.int_)
        np.random.shuffle(order)
        for i in order:
            acc.add(i)
            assert len(acc) <= 10

        topn = []
        # start with the smallest remaining one, grab!
        while len(acc) > 0:
            topn.append(acc.remove())

        topn = np.array(topn)
        xs = np.argsort(values)
        assert all(topn == xs[-10:])


def test_zero_empty():
    buf = np.empty(0)
    lkcu.zero_buf(buf)
    assert len(buf) == 0


def test_zero_one():
    buf = np.full(1, 1, dtype=np.float_)
    lkcu.zero_buf(buf)
    assert buf[0] == 0


def test_zero_many():
    buf = np.random.randn(100)
    lkcu.zero_buf(buf)
    assert len(buf) == 100
    assert all(buf == 0)
