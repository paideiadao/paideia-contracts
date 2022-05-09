from dataclasses import dataclass
from ergo_python_appkit.appkit import ErgoAppKit
from .. import staking

@dataclass
class StakingConfig:
    appKit: ErgoAppKit
    stakeStateNFT: str
    stakePoolNFT: str
    emissionNFT: str
    stakeTokenId: str
    stakedTokenId: str
    stakePoolKey: str
    stakedTokenName: str
    stakedTokenDecimals: int
    stakeStateContract: staking.StakeStateContract = None
    stakePoolContract: staking.StakePoolContract = None
    emissionContract: staking.EmissionContract = None
    stakeContract: staking.StakeContract = None
    stakeProxyContract: staking.StakeProxyContract = None
    addStakeProxyContract: staking.AddStakeProxyContract = None
    unstakeProxyContract: staking.UnstakeProxyContract = None
    stakingIncentiveContract: staking.StakingIncentiveContract = None

def PaideiaTestConfig(appKit: ErgoAppKit) -> StakingConfig:
    result = StakingConfig()
    result.appKit = appKit
    result.stakeStateNFT = "efdcb8ec05cf4da345530293860fa4b7106575fd6c2acc91a4e951e8b195c01f"
    result.stakePoolNFT = "56aa0514bae0abaa32f93af1c5f50e41fb0146abc8aeef6c6f710bc3c9986b58"
    result.emissionNFT = "8b9afefb32e2a6ad9c622d49826afb458c3f329a433a1bf928208f25f43fb734"
    result.stakeTokenId = "91e6e1e2e9a35a16848c66d58ac100be0112024016922e4783825183396efe0a"
    result.stakedTokenId = "c9cce92efe5beb4253456b0ccf3bb97ce5ddcf69fb382c2a00722f33bd97eb46"
    result.stakePoolKey= "6605390819ab84f716d808874ac1f48ea9cc43526a81262210ffb6177eb2ce63"
    result.stakedTokenName = "Paideia Test"
    result.stakedTokenDecimals = 4
    result.stakeContract = staking.StakeContract(result)
    result.stakeStateContract = staking.StakeStateContract(result)
    result.stakePoolContract = staking.StakePoolContract(result)
    result.emissionContract = staking.EmissionContract(result)
    result.stakingIncentiveContract = staking.StakingIncentiveContract(result)
    result.stakeProxyContract = staking.StakeProxyContract(result)
    result.addStakeProxyContract = staking.AddStakeProxyContract(result)
    result.unstakeProxyContract = staking.UnstakeProxyContract(result)
    return result