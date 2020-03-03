from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from io import open
from builtins import map
from builtins import range
from builtins import chr
from builtins import str
from future import standard_library
standard_library.install_aliases()
import os
import re

from .File import File, WrongFormatError
import numpy as np
import pandas as pd


class HAWCStab2IndFile(File):

    @staticmethod
    def defaultExtensions():
        return ['.ind', '.txt']

    @staticmethod
    def formatName():
        return 'HAWCStab2 induction file'

    def _read(self, *args, **kwargs):
        # Reading header line
        with open(self.filename,'r',encoding=self.encoding) as f:
            header = f.readline().strip()
        if len(header)<=0 or header[0]!='#':
            raise WrongFormatError('Ind File {}: header line does not start with `#`.'.format(self.filename)+e.args[0])
        # Extracting column names
        header       = '0 '+header[1:].strip()
        num_and_cols = [s.strip()+']' for s in header.split(']')[:-1]]
        cols         = [(' '.join(col.split(' ')[1:])).strip().replace(' ','_')  for col in num_and_cols]
        # Determining type based on number of columns (NOTE: could use col names as well maybe)
        NumCol2Type = {38: 'ind', 14: 'fext', 18: 'defl'}
        try:
            self.type = NumCol2Type[len(cols)]
        except Exception as e:    
            raise WrongFormatError('Ind File {}: '.format(self.filename))
        self.colNames=cols

        # Reading numerical data
        try:
            self.data = np.loadtxt(self.filename, skiprows=1)
        except Exception as e:    
            raise BrokenFormatError('Ind File {}: '.format(self.filename)+e.args[0])

        if self.data.shape[1]!=len(cols):
            raise BrokenFormatError('Ind File {}: inconsistent number of header columns and data columns.'.format(self.filename)+e.args[0])

        # Extracting wind speed from filename 
        self.wsp = float(self.filename.lower().split('_')[-1].rstrip('.ind').lstrip('u'))/1000

    def _toDataFrame(self):
        key = '{:s} - ws={:06.3f}'.format(self.type,self.wsp)
        df= pd.DataFrame(data=self.data, columns=self.colNames)
        df.columns.name=key
        return df
        #dfs = {key: pd.read_csv(self.filename, delim_whitespace=True, names=cols, skiprows=1)}
        #return dfs
