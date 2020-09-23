from datetime import datetime as dt
import pandas as pd
import numpy as np
from scipy.optimize import fsolve
from price_scrapper import PScrapper

#To Do:
# * Discard cash flows with negative time intervals
# * Add comission option.
# * Improve file handle
# * Improve handling of coupon periods in mdur
# * Improve handling of "D" kind and names.
# * Improve handling of sites for scrapping

class Arbonds:

    names = ["AL29", "AL30", "AL35", "AE38", "AL41"]

    def __init__(self):
        self.prices = {}
        self.date = None
        self.bond_cfs = {}
        self.bond_irr = {}
        self.macaulay = {}
        self.bond_mdur = {}
        self.summary = None
        
    def update(self, site="rava", dkind=True):
        self.set_bond_prices(site=site, dkind=dkind)
        self.set_summary(site=site, dkind=dkind)

    def read_csv(self, arch):
        """Reads bond interest and principal payments"""
        path = "data/" + arch
        df = pd.read_csv(path, names=['fecha', 'i', 'A'])
        df['fecha']=pd.to_datetime(df.fecha, format="%d/%m/%y")
        df.set_index("fecha", inplace=True)
        return df
        
    def npv(self, i_rate, cash_flows, years):
        """Returns Net Present Value for an array of cashflows and times given
        an interest rate i_rate. cash_flwos and years must be numpy arrays"""
        return np.sum(cash_flows / ( 1 + i_rate ) ** years)
    
    def include_purchase_cfs(self, bond_df, i, R, date=None):
        """Completes the bond cash flows with purchase data. This method
        inserts an interest i and principal R at given date. If date is None,
        then date = datetime.now()"""
        
        #  If not given, set date to now
        if date is None:
            date=dt.now()
            
        #  Include purchase data in cashflows
        df = bond_df
        df.loc[date]=[i, R]
        df.sort_index(inplace=True)
        return df
        
    def get_yrs_array(self, df):
        """Returns a numpy array with the time of each cashflow (in years)
        since first one"""
        years_raw = df.index.to_series().subtract(df.index[0]).values
        years_raw = years_raw/(60*60*24*365)
        return np.array([i * 1e-9 for i in years_raw.astype(float)])

    def get_cfs_array(self, bond_df):
        """Given a bond dataframe, returns the implied array of cashflows"""
        return (bond_df.i + bond_df.A).values
        
    def compute_irr(self, cash_flows, years, x0):
        """Computes IRR for given cash_flows"""
        return np.asscalar(fsolve(self.npv, 
                                  x0=x0, 
                                  args=(cash_flows, years)))
    
    def get_bond_irr(self, bond_df, guess=0.10):
        """Given a dataframe of bond cashflows, cumpute the implied irr.
        'guess' is the initial irr guess for the iteration"""
        cfs = self.get_cfs_array(bond_df)
        yrs = self.get_yrs_array(bond_df)
        return self.compute_irr(cfs, yrs, guess)
    
    def set_bond_prices(self, site, ticker_list=None, dkind=True):
        """Returns prices of bond taken from 'site' using PScrapper.
        if dkind, then append "D" to tickers"""
        if ticker_list is None:
            if dkind:
                ticker_list = [i + "D" for i in self.names]
            else:
                ticker_list = self.names
        ps = PScrapper()
        val_dict = ps.scrap(site, ticker_list)
        if dkind:
            for k, v in val_dict.items():
                self.prices[k[:-1]] = v
        else:
            self.prices = val_dict
        self.date = dt.now()
    
    def set_bond_cfs(self, site, dkind=True, log=True):
        """Si no es especie D, debo dolarizar los precios"""
        if log:
            print("Getting prices from " + str(site))
        self.set_bond_prices(site=site, dkind=dkind)
        
        if log:
            print("Computing cashflows")
        for ticker in self.names:
            price = self.prices[ticker]
            df_raw = self.read_csv(ticker + ".DAT")
            df = self.include_purchase_cfs(df_raw, 0, -price)
            self.bond_cfs[ticker] = df
        
    def set_bond_irr(self, site="rava", dkind=True):
        """For each bond, calculates irr using info in self.bond_cfs"""
        if self.bond_cfs == {}:
            self.set_bond_cfs(site=site, dkind=dkind)
        for ticker in self.names:
            self.bond_irr[ticker] = self.get_bond_irr(self.bond_cfs[ticker])
            
    def get_macaulay_dur(self, bond_df, irr):
        """Given a bond cash flows dataframe, and a yield, 
        this method finds the Macaulay duration"""
        cfs = self.get_cfs_array(bond_df)
        yrs = self.get_yrs_array(bond_df)
        npv = self.npv(irr,cfs[1:], yrs[1:])
        acum = 0
        for i in range(len(cfs)):
            acum = acum + self.npv(irr, cfs[i], yrs[i])*yrs[i]
        return acum/npv
        
    def set_bond_macaulay(self, site="rava", dkind=True):
        """Sets the value of self.macaulay as a dict of Macaulay
        durations for each bond"""
        if self.bond_irr == {}:
            self.set_bond_irr(site=site, dkind=dkind)
        for ticker in self.names:
            bdf = self.bond_cfs[ticker]
            irr = self.bond_irr[ticker]
            self.macaulay[ticker] = self.get_macaulay_dur(bdf, irr)

    def set_bond_mdur(self, site="rava", dkind=True, periods=2.0):
        """Sets the value of self.bond_mdur as a dict of modified durations
        for each bond"""
        if self.macaulay == {}:
            self.set_bond_macaulay(site=site, dkind=dkind)
        for ticker in self.names:
            self.bond_mdur[ticker] = self.macaulay[ticker] / (1 + 
                self.bond_irr[ticker]/periods)

    def set_summary(self, site, dkind=True):
        """Creates a dataframe with summary information and stores it
        in self.summary dataframe"""
        if self.bond_mdur == {}:
            self.set_bond_mdur(site=site, dkind=dkind)
        summary = {}
        for ticker in self.names:
            summary[ticker]=[self.date,
                             self.prices[ticker],
                             self.bond_irr[ticker],
                             self.bond_mdur[ticker]]
        df = pd.DataFrame(summary).T
        df.columns = ["date", "price", "IRR", "MDur"]
        self.summary = df

