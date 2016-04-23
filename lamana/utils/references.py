#------------------------------------------------------------------------------
'''A class for storing weblinks and references for package development.'''


class Reference(object):
    '''A non-functional class containing urls for supporting code.'''

    # ----- ---------                           -------------
    # (001) imp.relaod                          http://stackoverflow.com/questions/961162/reloading-module-giving-error-reload-is-not-defined
    # (002) __float__ magic method              http://www.rafekettler.com/magicmethods.html
    # (003) Use all() for conditional testing   http://stackoverflow.com/questions/10666163/how-to-check-if-all-elements-of-a-list-matches-a-condition
    # (004) Prevent __getattr__ recursuion      http://stackoverflow.com/questions/11145501/getattr-going-recursive-in-python
    # (005) Cautions with using super()         https://fuhm.net/super-harmful/
    # (006) dict to DataFrame                   http://pandas.pydata.org/pandas-docs/version/0.15.2/dsintro.html#from-a-list-of-dicts
    # (007) f(x) to rearrange columns           http://stackoverflow.com/questions/12329853/how-to-rearrange-pandas-column-sequence
    # (008) Exception handling Python 3         https://docs.python.org/3/reference/simple_stmts.html
    # (009) List of Exceptions                  http://www.tutorialspoint.com/python/python_exceptions.htm
    # (010) Panadas slicing negative indices    https://github.com/pydata/pandas/issues/2600
    # (011) Count words in column               http://stackoverflow.com/questions/17573814/count-occurrences-of-certain-words-in-pandas-dataframe
    # (012) groupby .first()                    http://pandas.pydata.org/pandas-docs/stable/groupby.html
    # (013) Read files from directory           https://stackoverflow.com/questions/15994981/python-read-all-files-from-folder-shp-dbf-mxd-etc
    # (014) DataFrame equal by Quant            https://stackoverflow.com/questions/14224172/equality-in-pandas-dataframes-column-order-matters
    # (015) Testing in pandas                   http://pandas.pydata.org/developers.html#how-to-write-a-test
    # (016) How to skip N/A as nan              http://pandas.pydata.org/pandas-docs/dev/generated/pandas.io.parsers.read_csv.html
    # (017) Default na values                   http://pandas.pydata.org/pandas-docs/stable/io.html#na-values
    # (018) Make smaller chunks from a list     https://stackoverflow.com/questions/312443/how-do-you-split-a-list-into-evenly-sized-chunks-in-python
    # (019) Laminar Composites                  Staab, G.  Butterworth-Heineman. 1999.
    # (020) Inverted cumsum()                   https://stackoverflow.com/questions/16541618/perform-a-reverse-cumulative-sum-on-a-numpy-array
    # (021) groupby cumsum()                    https://stackoverflow.com/questions/15755057/using-cumsum-in-pandas-on-group
    # (022) Select numeric columns              https://stackoverflow.com/questions/25039626/find-numeric-columns-in-pandas-python
    # (023) Dynamic module import               https://stackoverflow.com/questions/301134/dynamic-module-import-in-python
    # (024) Test Exceptions                     https://stackoverflow.com/questions/7799593/how-an-exceptions-be-tested-with-nose
    # (025) Print exception traceback; no halt  https://stackoverflow.com/questions/3702675/how-to-print-the-full-traceback-without-halting-the-program
    # (026) Extract number from string          https://stackoverflow.com/questions/4289331/python-extract-numbers-from-a-string
    # (027) Natural sort                        https://stackoverflow.com/questions/2545532/python-analog-of-natsort-function-sort-a-list-using-a-natural-order-algorithm
    # (028) Overload __eq__                     http://jcalderone.livejournal.com/32837.html
    # (029) DataFrames to image                 https://stackoverflow.com/questions/26678467/export-a-pandas-dataframe-as-a-table-image#
    # (030) setter properties                   https://stackoverflow.com/questions/1684828/how-to-set-attributes-using-property-decorators
    # (031) multiprocessing vs threading        http://sebastianraschka.com/Articles/2014_multiprocessing_intro.html
    # (032) Intro on multiprocessing            http://toastdriven.com/blog/2008/nov/11/brief-introduction-multiprocessing/
    # (033) Subclassing a dict                  https://stackoverflow.com/questions/21361106/how-would-i-implement-a-dict-with-abstract-base-classes-in-python
    # (034) Slice a dict                        http://pythoncentral.io/how-to-slice-custom-objects-classes-in-python/
    # (035) Implement __hash__                  https://stackoverflow.com/questions/4005318/how-to-implement-a-good-hash-function-in-python
    # (036) Check if file exists                https://stackoverflow.com/questions/82831/check-whether-a-file-exists-using-python
    # (037) Make list of alphabet               http://snipplr.com/view/5058/
    # (038) Annotate rectangle layers           https://stackoverflow.com/questions/14531346/how-to-add-a-text-into-a-rectangle
    # (039) regex Lookarounds                   http://www.rexegg.com/regex-lookarounds.html#overlapping
    # (040) pyregex                             http://www.pyregex.com/
    # (041) regex search                        http://stackoverflow.com/questions/1323364/in-python-how-to-check-if-a-string-only-contains-certain-characters
    # (042) Example of regex patterns           https://hg.python.org/cpython/file/2.7/Lib/tokenize.py#l108
    # (043) Interactive, regex visualization    https://regex101.com/r/lL0cW7/4
    # (044) regex to find comma inside (),[]    https://stackoverflow.com/questions/33793037/python-regex-to-find-special-characters-between-delimiters/33793322#33793322
    # (045) Good integreation practices         https://pytest.org/latest/goodpractises.html
    # (046) sorted with a key                   http://www.thegeekstuff.com/2014/06/python-sorted/
    # (047) Force create directory              https://stackoverflow.com/questions/273192/in-python-check-if-a-directory-exists-and-create-it-if-necessary
    # (048) Deprecation of __getslice__         https://docs.python.org/2/reference/datamodel.html#additional-methods-for-emulation-of-sequence-types
    # (049) Axes and Figure plots in seaborn    http://stackoverflow.com/questions/23969619/plotting-with-seaborn-using-the-matplotlib-object-oriented-interface
    # (050) DISPLAY variable error              https://stackoverflow.com/questions/2801882/generating-a-png-with-matplotlib-when-display-is-undefined

    pass
#------------------------------------------------------------------------------

class RegexLinks(object):
    '''A non-functional class containing urls for regular expressions.'''

    # ----- ---------                           -------------
    # (001) Inners, not duples                  http://pythex.org/?regex=(%3F%3C!%5B(%5Cd%2B%5D)(%5Cd*%5C.*%5Cd*%20*%5C%2C*%3F)(%3F!%5B%5Cd%5C.)%5D)&test_string=0%0A1%0A1.%0A10%0A10.%0A100%0A10.0%0A100.0%0A1000.0%0A1S%0A1.S%0A1.0S%0A%5B100%5D%0A%5B100.%5D%0A%5B100.0%5D%0A%5B100%2C100%5D%0A%5B100.%2C100.%5D%0A%5B100.0%2C100.0%5D%0A%5B100.0%2C100%5D%0A%5B100%2C%20(100%2C100)%5D&ignorecase=0&multiline=0&dotall=0&verbose=0
