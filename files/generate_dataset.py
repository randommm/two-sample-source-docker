import numpy as np
import pandas as pd

np.random.seed(12)
MCD = np.random.normal(0.6737, 0.1163, 45) * 57 +  50
AD = np.random.normal(0.4716, 0.2042, 52) * 57 +  50
CG = np.random.normal(0.8376, 0.0941, 39) * 57 +  50

camcog = np.array(np.concatenate([MCD, AD, CG]), dtype=np.int0)
diag = np.concatenate([np.repeat("MCD", 45), np.repeat("AD", 52),
                       np.repeat("CG", 39)])

dataf = pd.DataFrame(np.column_stack([diag, camcog]))
dataf.to_csv("data.csv", header=["diag", "CAMCOG"], index=False)
