# model.py
# Bu program, XGBoost modelini eğitmek için kullanılır.

# Gerekli kütüphanelerin import edilmesi
import pandas as pd
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score

# Verinin okunması
data = pd.read_csv('input.csv')

# Özellikler ve hedef değişkenin ayrılması
X = data.drop('target_column', axis=1)
y = data['target_column']

# Verinin eğitim ve test setlerine ayrılması
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# XGBoost modelinin oluşturulması
model = XGBClassifier()

# Modelin eğitilmesi
model.fit(X_train, y_train)

# Tahminlerin yapılması
y_pred = model.predict(X_test)

# Doğruluk oranının hesaplanması
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy: %.2f%%" % (accuracy * 100.0))

# Program sona erdi.