# HTS Reader #

```
>>> from hts_reader.h_model import HMMSet
>>> hmm_set = HMMSet()
>>> hmm_set.read("examples/test.mmf", forced=True)
>>> hmm_set.read("cat examples/test.mmf|", forced=True)
>>> hmm_set.read(forced=True, from_stdin=True)
```

This module allows to read the HTS binary model from file, stdin, or even pipeline.
The pipeline can be a HHEd command.

I wrote this module with in a similar way with HModel.c. So if you want to improve it,
it is necessary to read the HModel.c first. It should not be too hard.

# Support Macros #
Currently, this version support the following macros: o, t, v, m, s, p, h.
I will try to add more macro in the future. But it should be too hard to do it by yourself.

# Requirements #
* [py_io](https://bitbucket.org/truongdq/python_io/) - supports reading from stdin, pipeline
