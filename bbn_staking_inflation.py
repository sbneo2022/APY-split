import streamlit as st
import pandas as pd


class StakingSimulator:
    def __init__(self, TVL, FDV, StakingRatio, BBNPrice, TotalBBN, InflationRate, BTCSplit, BBNSplit, btc_staking_apr, lrt2_rewards_apr, estimated_s4_added_apr, collateral_yield, borrow_cost, ltv_ratio, max_leverage):
        self.TVL = TVL
        self.FDV = FDV
        self.StakingRatio = StakingRatio
        self.BBNPrice = BBNPrice
        self.TotalBBN = TotalBBN
        self.InflationRate = InflationRate
        self.BTCSplit = BTCSplit
        self.BBNSplit = BBNSplit
        self.btc_staking_apr = btc_staking_apr
        self.lrt2_rewards_apr = lrt2_rewards_apr
        self.estimated_s4_added_apr = estimated_s4_added_apr
        self.collateral_yield = collateral_yield
        self.borrow_cost = borrow_cost
        self.ltv_ratio = ltv_ratio
        self.max_leverage = max_leverage

    def calculate_Sstaked(self):
        return self.TotalBBN * self.StakingRatio

    def calculate_Rinf(self):
        return self.InflationRate * self.TotalBBN * self.BBNPrice

    def calculate_RBTC(self):
        return self.calculate_Rinf() * self.BTCSplit / 100

    def calculate_RBBN(self):
        return self.calculate_Rinf() * self.BBNSplit / 100

    def calculate_TBTC(self):
        return self.TVL * self.BTCSplit / 100

    def calculate_VBBN(self):
        return self.calculate_Sstaked() * self.BBNPrice

    def calculate_BTCAPY(self):
        return self.BTCSplit * self.InflationRate * self.TotalBBN * self.BBNPrice / self.TVL 
    
    def calculate_BBNAPY(self):
        return self.calculate_RBBN() / self.calculate_VBBN() * 100

    def calculate_apr_without_s4(self):
        total_apr_without_s4 = self.btc_staking_apr + self.lrt2_rewards_apr + self.collateral_yield
        return total_apr_without_s4
    
    def calculate_net_apr_without_s4(self):
        net_apr_without_s4 = self.calculate_apr_without_s4() - self.borrow_cost
        return net_apr_without_s4
    
    def calculate_leveraged_apr_without_s4(self):
        leveraged_apr_without_s4 = self.calculate_net_apr_without_s4() * self.max_leverage
        return leveraged_apr_without_s4


from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class SimulatorInputs:
    TVL: float
    FDV: float
    StakingRatio: float
    BBNPrice: float
    TotalBBN: float
    InflationRate: float
    BTCSplit: float
    BBNSplit: float
    btc_staking_apr: float
    lrt2_rewards_apr: float
    estimated_s4_added_apr: float
    collateral_yield: float
    borrow_cost: float
    ltv_ratio: float
    max_leverage: float

class SimulatorUI(ABC):
    @abstractmethod
    def setup_page(self):
        pass
    
    @abstractmethod
    def get_inputs(self) -> SimulatorInputs:
        pass
    
    @abstractmethod
    def display_results(self, btc_apy: float, bbn_apy: float):
        pass

class StreamlitUI(SimulatorUI):
    def setup_page(self):
        st.set_page_config(page_title="Staking Simulator", layout="wide")
        st.title("Staking Simulator for Bitcoin and Babylon Stakers")
        
    def get_inputs(self) -> SimulatorInputs:
        st.sidebar.header("Input Parameters")
        TVL = st.sidebar.number_input("Total Value Locked (TVL) in USD", value=10000000000)
        FDV = st.sidebar.number_input("Fully Diluted Value (FDV) in USD", value=4000000000)
        StakingRatio = st.sidebar.slider("Staking Ratio", min_value=0.0, max_value=1.0, value=0.4)
        BBNPrice = st.sidebar.number_input("Price of 1 BBN token in USD", value=0.4)
        TotalBBN = st.sidebar.number_input("Total supply of BBN tokens", value=10000000000)
        InflationRate = st.sidebar.slider("Annual Inflation Rate (%)", min_value=0.0, max_value=100.0, value=8.0)
        BTCSplit = st.sidebar.slider("BTC Split (%)", min_value=0.0, max_value=100.0, value=50.0)
        st.sidebar.write(f"BBN Split: {100 - BTCSplit}%")
        BBNSplit = 100 - BTCSplit
        
        
        btc_staking_apr = st.sidebar.number_input("BTC Staking APR (%)", min_value=0.0, value=1.6, step=0.01)
        lrt2_rewards_apr = st.sidebar.number_input("LRT2 Rewards APR (%)", min_value=0.0, value=0.6, step=0.01) 
        estimated_s4_added_apr = st.sidebar.number_input("Estimated S4 Added APR (%)", min_value=0.0, value=0.5, step=0.01)
        collateral_yield = st.sidebar.number_input("Collateral Yield (%)", min_value=0.0, value=0.01, step=0.01)
        borrow_cost = st.sidebar.number_input("Borrow Cost (%)", min_value=0.0, value=1.0, step=0.01)
        ltv_ratio = st.sidebar.slider("Loan-to-Value Ratio (LTV)", min_value=0.0, max_value=100.0, value=75.0, step=0.1)
        max_leverage = st.sidebar.number_input("Max Leverage", min_value=1.0, value=4.0, step=0.1)
        
        

        
        
        return SimulatorInputs(
            TVL=TVL,
            FDV=FDV,
            StakingRatio=StakingRatio,
            BBNPrice=BBNPrice,
            TotalBBN=TotalBBN,
            InflationRate=InflationRate/100,
            BTCSplit=BTCSplit,
            BBNSplit=BBNSplit,
            btc_staking_apr=btc_staking_apr,
            lrt2_rewards_apr=lrt2_rewards_apr,
            estimated_s4_added_apr=estimated_s4_added_apr,
            collateral_yield=collateral_yield,
            borrow_cost=borrow_cost,
            ltv_ratio=ltv_ratio,
            max_leverage=max_leverage
        )
    
    def display_results(self, btc_apy: float, bbn_apy: float, apr_without_s4: float, net_apr_without_s4: float, leveraged_apr_without_s4: float):
        st.header("Results")
        st.markdown(f"**BTC APR:** {btc_apy:.3f}%")
        st.markdown(f"**BBN APR:** {bbn_apy:.3f}%")
        st.markdown(f"**Total APR Without S4:** {apr_without_s4:.3f}%")
        st.markdown(f"**Net APR Without S4:** {net_apr_without_s4:.3f}%")
        st.markdown(f"**Leveraged APR Without S4:** {leveraged_apr_without_s4:.3f}%")

        df = pd.DataFrame({"APR": [btc_apy, bbn_apy]}, index=["BTC", "BBN"])




if __name__ == "__main__":
    # Initialize and run
    ui = StreamlitUI()
    ui.setup_page()
    inputs = ui.get_inputs()
    simulator = StakingSimulator(
        inputs.TVL, inputs.FDV, inputs.StakingRatio, 
        inputs.BBNPrice, inputs.TotalBBN, inputs.InflationRate,
        inputs.BTCSplit, inputs.BBNSplit, inputs.btc_staking_apr, inputs.lrt2_rewards_apr, inputs.estimated_s4_added_apr, inputs.collateral_yield, inputs.borrow_cost, inputs.ltv_ratio, inputs.max_leverage
    )

    btc_apy = simulator.calculate_BTCAPY()
    bbn_apy = simulator.calculate_BBNAPY()
    apr_without_s4 = simulator.calculate_apr_without_s4()
    net_apr_without_s4 = simulator.calculate_net_apr_without_s4()
    leveraged_apr_without_s4 = simulator.calculate_leveraged_apr_without_s4()
    ui.display_results(btc_apy, bbn_apy, apr_without_s4, net_apr_without_s4, leveraged_apr_without_s4)
