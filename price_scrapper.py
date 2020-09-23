from urllib.request import urlopen
from lxml import etree
import numpy as np

#response = urlopen("http://www.rava.com/empresas/perfil.php?e=AL29D")

class PScrapper:
    site = {'rava' : {'url': 'http://www.rava.com/empresas/perfil.php?e=',
                      'xpath':'//td/span/text()',
                      'loc':0}
           }
                      
    def __init__(self):
        self.htmlparser = etree.HTMLParser()
        
    def scrap(self, site, list_tickers):
        results = {}
        for ticker in list_tickers:
            response = urlopen(self.site[site]['url'] + ticker)
            tree = etree.parse(response, self.htmlparser)
            res = tree.xpath(self.site[site]['xpath'])
            value_raw = res[self.site[site]['loc']].replace(",", ".")
            results[ticker] = self.myfloat(value_raw)
        return results
        
    def myfloat(self, value):
        """Encapsulates np.float"""
        try:
            myfloat = np.float(value)
        except:
            myfloat = np.nan
        return myfloat