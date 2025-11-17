import xgboost as xgb
booster = xgb.Booster()
booster.load_model("models/xgb_model.json")
print(booster.attributes())
