# region imports
from AlgorithmImports import *
from datetime import datetime
# endregion

class MacroLiquidityStrategy(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2022, 3, 12)
        self.set_end_date(datetime.now())
        self.set_cash(100000)

        self.universe_settings.resolution = Resolution.DAILY
        self.add_universe(self.coarseSelection, self.fineSelection)

        self.fedRateSymbol = self.add_data(Fred, "FEDFUNDS", Resolution.DAILY).symbol
        self.balance_sheet_symbol = self.add_data(Fred, "WALCL", Resolution.DAILY).symbol

        self.stockBuckets = {'A':[], 'B&C':[], 'D':[]}

        '''self.schedule.on(
            self.date_rules.week_start(),
            self.time_rules.at(10,0),
            self.rebalance
        )'''

        self.selectedSymbols = []
        self.currentRegime = None

        self.set_benchmark("SPY")
    
    
    def coarseSelection(self,coarse):
        filtered = [stock for stock in coarse if stock.has_fundamental_data and stock.market == "usa"]
        return [stock.symbol for stock in sorted(filtered,key=lambda x: x.dollar_volume, reverse=True)[:1000]]

    def fineSelection(self,fine):

        self.stockBuckets = {'A': [], 'B&C': [], 'D': []}
        
        for stock in fine:
            try:
                pe = stock.valuation_ratios.pe_ratio
                debt = stock.financial_statements.balance_sheet.total_debt.twelve_months
                ebitda = stock.financial_statements.income_statement.ebitda.twelve_months
                debtEbitda = debt / ebitda if ebitda and ebitda != 0 else None
                revenueGrowth = stock.operation_ratios.revenue_growth.value
                volume = stock.dollar_volume

                if None in (pe,revenueGrowth,revenueGrowth,debtEbitda):
                    continue

                if revenueGrowth <=0.05 and pe<13 and debtEbitda<1.5:
                    self.stockBuckets['A'].append((stock.symbol,volume))
                
                elif revenueGrowth >0.5:
                    self.stockBuckets['D'].append((stock.symbol,volume))
                
                elif revenueGrowth >=0.1 and revenueGrowth <=0.2 and debtEbitda <=5 and pe<=25:
                    self.stockBuckets['B&C'].append((stock.symbol,volume))
                
            except Exception as e:
                continue

        selected = []
        for bucket in ['A','B&C','D']:
            self.stockBuckets[bucket] = sorted(self.stockBuckets[bucket], key = lambda x:x[1],reverse = True)
            selected.extend([symbol for symbol, _ in self.stockBuckets[bucket][:10]])
            
        return selected
    
    def getLiquidity(self):
        balanceSheetHistory = self.history(self.balance_sheet_symbol,30,Resolution.DAILY)
        rateHistory = self.history(self.fedRateSymbol,10,Resolution.DAILY)

        if balanceSheetHistory.empty or rateHistory.empty:
            return "neutral"
        
        bsNow = balanceSheetHistory["value"].iloc[-1]
        bs4w = balanceSheetHistory["value"].iloc[0]
        rateNow = rateHistory["value"].iloc[-1]

        balanceTrend = "increasing" if bsNow > bs4w else "decreasing"

        if rateNow <1.5:
            rateLevel = "low"
        
        elif rateNow >4.5:
            rateLevel = "high"
        
        else:
            rateLevel = "medium"
        
        if balanceTrend == "increasing" and rateLevel == "low":
            return "most_liquid"
        
        elif balanceTrend == "decreasing" and rateLevel == "high":
            return "least_liquid"
        
        else:
            return "neutral"
    
    def rebalance(self):
        liquidity = self.getLiquidity()

        if liquidity == "most_liquid":
            selected = selected = [symbol for symbol, _ in self.stockBuckets['D'][:5]]
        
        elif liquidity == "least_liquid":
            selected = selected = [symbol for symbol, _ in self.stockBuckets['A'][:5]]
        
        else:
            selected = selected = [symbol for symbol, _ in self.stockBuckets['B&C'][:5]]
        
        if not selected:
            return
        
        weight = 1/len(selected)

        for symbol in self.portfolio:
            if symbol.key not in selected and self.portfolio[symbol.key].invested:
                self.liquidate(symbol.key)
                self.debug(f"Liquidating {symbol.key}")
            
        for symbol in selected:
            self.set_holdings(symbol,weight)
            self.debug(f"Buying {symbol} with weight {weight}")
    
    def on_securities_changed(self,changes):
        self.rebalance()


