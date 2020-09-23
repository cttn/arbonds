from urllib.request import urlopen
from lxml import etree
import numpy as np


class PScrapper:
    site = {'rava' : {'url': 'http://www.rava.com/empresas/perfil.php?e=',
                      'xpath':'//td/span/text()',
                      'loc':0},
            'eco' : {'url': 'http://bonos.ecobolsar.com.ar/eco/ticker.php?t=',
                    'xpath':"//td[@class='precioticker']/text()",
                    'loc': 0}
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