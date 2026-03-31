# 🧠 AI Academic Intelligence - Backend

A Django-based backend system designed to analyze student academic performance and predict future risks using Machine Learning.

---

## 🚀 Features

* 👨‍🎓 Student, Staff, Department & Batch Management
* 📊 Subject & Topic-wise performance tracking
* 📈 CO (Course Outcome) mapping
* 📝 Exam & Marks management (IAT, Model, SEM)
* 🤖 ML-based **Failure Prediction System**
* 📅 AI-powered Study Plan generation
* 📉 Identify weak & strong students

---

## 🏗️ Tech Stack

* **Backend**: Django, Django REST Framework
* **Database**: SQLite (can be upgraded to PostgreSQL)
* **Machine Learning**: Scikit-learn (Random Forest)
* **Language**: Python

---

## 📂 Project Structure

```
myapp/
│
├── intelligence/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   ├── ml_engine/
│   │   ├── dataset.py       # Build dataset from DB
│   │   ├── train.py         # Train ML model
│   │   ├── predict.py       # Prediction logic
│   │   ├── model.pkl        # Saved trained model
│
├── myapp/
│   ├── settings.py
│   ├── urls.py
│
├── manage.py
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone <your-repo-url>
cd your-repo
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5️⃣ Run Server

```bash
python manage.py runserver
```

---

## 🤖 Machine Learning Module

### 📊 Dataset

* Extracted from:

  * `Student`
  * `StudentMarks`
  * `StudentExam`

* Current Logic:

  * Uses **IAT1 → Predict IAT2 Failure**

---

### 🏋️ Train Model

```bash
python manage.py shell
```

```python
from intelligence.ml_engine.train import train_model
train_model()
```

✔ Output:

* Model accuracy
* Saved model (`model.pkl`)

---

### 🔮 Prediction

```python
from intelligence.ml_engine.predict import predict_student

predict_student(iat1=35)
```

---

### 📤 Output Example

```json
{
  "prediction": 1,
  "fail_probability": 0.78
}
```

---

## 🧠 ML Workflow

1. Extract data from DB
2. Convert to dataset
3. Train Random Forest model
4. Save trained model
5. Predict future failures

---

## ⚠️ Important Notes

* Requires sufficient student marks data
* Better accuracy with:

  * Multiple batches
  * Multiple subjects
  * Complete exam records

---

## 🚀 Future Improvements

* Predict SEM using IAT1, IAT2, IAT3
* Add trend-based features
* CO-wise performance prediction
* LLM integration for AI feedback
* Real-time dashboard integration

---

## 👨‍💻 Author

**Bharath Sivanesh**
AI + Full Stack Developer

---

## 📌 License

This project is for educational purposes.
