# model.py

# Gerekli kütüphaneleri import ediyoruz
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_boston

# Veri setini yükleyelim ve değişkenlere atayalım
boston = load_boston()
X = boston.data
y = boston.target

# Veri setini eğitim ve test veri seti olarak ayırıyoruz
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=123)

# XGBoost modelini oluşturuyoruz
xg_reg = xgb.XGBRegressor(objective ='reg:linear', colsample_bytree = 0.3, learning_rate = 0.1,
                max_depth = 5, alpha = 10, n_estimators = 10)

# Modeli eğitiyoruz
xg_reg.fit(X_train,y_train)

# Eğitim veri setini kullanarak tahminler yapıyoruz
preds = xg_reg.predict(X_test)

# Tahminleri ve gerçek değerleri karşılaştırabiliriz
for i in range(5):
    print("Predicted:", preds[i], "Actual:", y_test[i])