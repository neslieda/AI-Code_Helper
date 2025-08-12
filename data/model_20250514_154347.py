# model.py

# Kütüphanelerin import edilmesi
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

# Veri setinin yüklenmesi
data = pd.read_csv('data.csv')

# Öznitelik ve hedef değişkenin belirlenmesi
features = data.drop('target', axis=1)
target = data['target']

# Veri setinin eğitim ve test seti olarak bölünmesi
X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=123)

# XGBoost modelinin oluşturulması
model = XGBRegressor(objective ='reg:squarederror', colsample_bytree = 0.3, learning_rate = 0.1,
                max_depth = 5, alpha = 10, n_estimators = 10)

# Modelin eğitilmesi
model.fit(X_train, y_train)

# Eğitilmiş modelin test verisi üzerinde tahmin yürütmesi
predictions = model.predict(X_test)

# Modelin performansının değerlendirilmesi
rmse = np.sqrt(mean_squared_error(y_test, predictions))
print("RMSE: %f" % (rmse))