import random
from celery import shared_task

from contract import models


@shared_task(name="contract_roi_generator")
def contract_roi_generator():
    for contract in models.Contract.objects.filter(
        contract_status=models.Contract.OPEN
    ):
        roi_rate = round(
            random.uniform(contract.roi_rate_from, contract.roi_rate_to), 4
        )
        models.ContractRoiLog.objects.create(roi_rate=roi_rate, contract=contract)
        contract.roi_daily_rate = roi_rate
        contract.save()
