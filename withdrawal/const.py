from account import models as account_models

WITHDRAWAL_ACCOUNTS = [
    account_models.Account.CREDIT,
    account_models.Account.SPONSOR,
    account_models.Account.TRADE,
    account_models.Account.TIERING,
]

WITHDRAWAL_BLOCKCHAIN = "blockchain"
WITHDRAWAL_BANK = "bank"
WITHDRAWAL_METHODS = [WITHDRAWAL_BLOCKCHAIN, WITHDRAWAL_BANK]
