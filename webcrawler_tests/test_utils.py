class FunctorTest():
    @staticmethod
    def test(test, functor, input, expected, **kwargs):
        test.assertEqual(expected, functor(input, **kwargs))