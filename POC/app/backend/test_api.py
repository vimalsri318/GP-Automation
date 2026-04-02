# import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.services.step2_service import parse_revenue, parse_cost

r_res = parse_revenue()
c_res = parse_cost()

print("Revenue:", r_res)
print("Cost:", c_res)
