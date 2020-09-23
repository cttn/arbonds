from datetime import datetime as dt
import pandas as pd
import numpy as np
from scipy.optimize import fsolve
from price_scrapper import PScrapper
#To Do:
# Ver cómo manejar intérvalos de tiempo negativos, que debería descartar
# del cálculo
# Agregar comision

class Arbonds:

    names = ["AL29","AL30","AL35","AE38","AL41"]

    def __init__(self):
        self.prices = None
        self.bond_cfs = {}
        self.bond_irr = {}
        self.macaulay = {}
        self.bond_mdur = {}
        
    def update(self, site="rava",especie_D=True):
        self.update_bond_mdur(site,especie_D)

    def read_csv(self,arch):
        """Reads bond interest and principal payments"""
        path = "data/" + arch
        df = pd.read_csv(path, names=['fecha','i','A'])
        df['fecha']=pd.to_datetime(df.fecha,format="%d/%m/%y")
        df.set_index("fecha",inplace=True)
        return df
        
    def npv(self, i_rate, cash_flows, years):
        """Returns Net Present Value for an array of cashflows and times given
        an interest rate i_rate. cash_flwos and years must be numpy arrays"""
        return np.sum(cash_flows / ( 1 + i_rate ) ** years)
    
    def include_purchase_cash_flow(self, bond_df, i, R, date=None):
        """Completes the bond cash flows with purchase data. This method
        insert an interest i and principal R at given date. If date is None,
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
        return np.array([i*1e-9 for i in years_raw.astype(float)])

    def get_cfs_array(self,bond_df):
        """Given a bond dataframe, returns the implied array of cashflows"""
        return cfs = (bond_df.i+bond_df.A).values
        
    def compute_irr(self, cash_flows, years, x0):
        """Computes IRR for given cash_flows"""
        return np.asscalar(fsolve(self.npv, 
                                  x0=x0, 
                                  args=(cash_flows, years)))
    
    def get_bond_irr(self, bond_df):
        """Given a dataframe of bond cashflows, cumpute the implied irr"""
        cfs = self.get_cfs_array(bond_df)
        yrs = self.get_yrs_array(bond_df)
        return self.compute_irr(cfs,yrs,0.10)
    
    def get_bond_prices(self, site, ticker_list=None, dkind=True):
        """Returns prices of bond taken from site using PScrapper.
        if dkind, then append "D" to tickers"""
        if ticker_list is None:
            if append_D:
                ticker_list = [i + "D" for i in self.names]
            else:
                ticker_list = self.names
        ps = PScrapper()
        values = ps.scrap(site,ticker_list)
        self.prices = values
        return None
    
    def update_bond_cfs(self,site,especie_D=True,log=True):
        """Si no es especie D, debo dolarizar los precios"""
        if log:
            print("Obteniendo precios desde " + str(site))
        self.get_prices(site)
        
        if log:
            print("Calculando cashflows")
        for i in range(len(self.names)):
            ticker = self.names[i]
            price = self.prices[i]
            df_raw = self.read_csv(ticker + ".DAT")
            df = self.true_cash_flows(df_raw,0,-price)
            self.bond_cfs[ticker] = df
        return None
        
    def update_bond_irr(self,site="rava",especie_D=True):
        """For each bond, calculates irr using info in self.bond_cfs"""
        if self.bond_cfs == {}:
            self.update_bond_cfs(site,especie_D=especie_D)
        for ticker in self.names:
            self.bond_irr[ticker] = self.get_bond_irr(self.bond_cfs[ticker])
        return None
            
    def get_macaulay_dur(self,bond_df,irr):
        cfs = (bond_df.i+bond_df.A).values
        yrs = self.years_diff(bond_df)
        npv = self.npv(irr,cfs[1:],yrs[1:])
        acum = 0
        for i in range(len(cfs)):
            acum = acum + self.npv(irr,cfs[i],yrs[i])*yrs[i]
        return acum/npv
        
    def update_bond_macaulay(self,site="rava",especie_D=True):
        if self.bond_irr == {}:
            self.update_bond_irr(site,especie_D)
        for ticker in self.names:
            bdf = self.bond_cfs[ticker]
            irr = self.bond_irr[ticker]
            self.macaulay[ticker] = self.get_macaulay_dur(bdf,irr)
        return None
        
    def update_bond_mdur(self,site="rava",especie_D=True,periods=2.0):
        if self.macaulay == {}:
            self.update_bond_macaulay(site,especie_D)
        for ticker in self.names:
            self.bond_mdur[ticker] = self.macaulay[ticker]/(1 + 
                self.bond_irr[ticker]/periods)
        return None
