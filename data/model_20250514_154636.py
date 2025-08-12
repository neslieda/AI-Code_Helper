# model.py

# Gerekli kütüphanelerin yüklenmesi
import pandas as pd
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Veri setinin yüklenmesi
dataset = pd.read_csv('dataset.csv')
# Veri setindeki özelliklerin ve hedef değişkenin belirlenmesi
X = dataset.drop('target', axis=1)
Y = dataset['target']

# Verinin eğitim ve test seti olarak ayrılması
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=7)

# XGBoost modelinin oluşturulması
model = XGBClassifier()

# Modelin eğitilmesi
model.fit(X_train, Y_train)

# Tahminlerin yapılması
y_pred = model.predict(X_test)

# Tahminlerin doğruluk oranının hesaplanması
accuracy = accuracy_score(Y_test, y_pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))