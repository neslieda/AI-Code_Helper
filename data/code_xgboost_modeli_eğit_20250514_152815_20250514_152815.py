import xgboost as xgb
from sklearn.model_selection import train_test_split

# Öncelikle, verilerinizi yüklemeniz ve ön işlemleri yapmanız gerekir. Burada 'X' özellikler matrisi, 'y' hedef vektörüdür
# X, y = load_data() 

# Verinizi eğitim ve test setlerine ayırın
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# XGBoost modelini başlatın
model = xgb.XGBClassifier()

# Modeli eğitim verileri ile eğitin
model.fit(X_train, y_train)

# Test verileri üzerinde tahmin yapın
y_pred = model.predict(X_test)