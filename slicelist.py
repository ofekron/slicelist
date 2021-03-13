class SliceList:
    class SliceListIterator:
        def __init__(self, lst):
            self.n = len(lst)
            self.lst = lst
            self.i = 0

        def __iter__(self):
            return self

        def __next__(self):
            if self.i >= self.n:
                raise StopIteration
            res = self.lst[self.i]
            self.i += 1
            return res

    def __init__(self, lst, slice_obj=None):
        self.__lst = lst if isinstance(lst, SliceList) or isinstance(lst, list) else list(lst)
        self.__originlen = len(self.__lst)
        if slice_obj is None:
            self.__left = 0
            self.__right = self.__len = self.__originlen
            self.__step = 1
            return

        if not isinstance(slice_obj, slice):
            raise ValueError(str(slice_obj) + " not a slice object")

        self.__step = slice_obj.step if slice_obj.step is not None else 1

        if self.__step == 0:
            raise ValueError("step cannot be zero")
        start = None if slice_obj.start is None else slice_obj.start if slice_obj.start >= 0 else self.__originlen + slice_obj.start
        stop = None if slice_obj.stop is None else slice_obj.stop if slice_obj.stop >= 0 else self.__originlen + slice_obj.stop
        if self.__step > 0:
            self.__left = start if start is not None else 0
            self.__right = stop if stop is not None else self.__originlen
            self.__len = (self.__right - self.__left) // self.__step
            if (self.__right - self.__left) % self.__step:
                self.__len += 1
        else:
            self.__right = start if start is not None else self.__originlen - 1
            self.__left = stop if stop is not None else -1
            self.__len = (self.__left - self.__right) // self.__step
            if (self.__left - self.__right) % -self.__step:
                self.__len += 1

        if self.__len < 0:
            self.__len = 0


    def __getitem__(self, key):
        if isinstance(key, slice):
            return SliceList(self, key)
        if not isinstance(key, int):
            raise NotImplemented("indexing for %s is not implemented" % str(key))
        if key < 0:
            if -key > self.__originlen:
                raise IndexError(key)
            key = self.__originlen + key

        if self.__step > 0:
            i = self.__left + key * self.__step

        else:
            i = self.__right + key * self.__step

        if i < 0 or i > self.__originlen:
            raise IndexError(key, 'slice=' + str({
                "left": self.__left,
                "right": self.__right,
                "step": self.__step,
                "len": self.__len,
            }))

        return self.__lst[i]

    def __len__(self):
        return self.__len

    def __repr__(self):
        return '[' + ",".join(map(str, self)) + ']'

    def explain(self):
        return 'slice=' + str({
            "left": self.__left,
            "right": self.__right,
            "step": self.__step,
            "len": self.__len,
        }) + '[' + ",".join(
            map(str, self)) + '] original :\n' + self.__lst.explain() if isinstance(self.__lst,
                                                                                    SliceList) else self.__lst.__repr__()

    def tolist(self):
        return list(self)

    def __iter__(self):
        return SliceList.SliceListIterator(self)


if __name__ == '__main__':
    from timeit import default_timer as timer


    def measure(to_measure):
        start = timer()
        res = to_measure()
        end = timer()
        return end - start, res


    def dummy_iter(it):
        for i in it:
            pass


    def print_ratio(action, n1, t1, n2, t2):
        print("%s : %s is faster then %s by factor of %.5f" % (
            action, n2 if t1 > t2 else n1, n1 if t1 > t2 else n2, t1 / t2 if t1 > t2 else t2 / t1))


    lst = list(range(1000000))
    check = [None] + list(range(-100, 100))
    slices = [slice(start, stop, step)
              for start in check
              for stop in check
              for step in check if step != 0
              ]
    for s in slices:
        print("slice : " + str(s))
        t1, a = measure(lambda: lst[s])
        t2, b = measure(lambda: SliceList(lst)[s])
        print_ratio("slicing", "list", t1, "slicelist", t2)

        t1, maxa = measure(lambda: max(a))
        t2, maxb = measure(lambda: max(b))
        print_ratio("max", "list", t1, "slicelist", t2)

        equals = a == b.tolist() and maxa == maxb
        if not equals:
            print(a)
            print(b.explain())
        assert equals
