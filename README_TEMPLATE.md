# Flight Price Prediction

## Project Description
This project aims to predict flight ticket prices using advanced machine learning techniques. By analyzing historical airline booking data, the system provides accurate fare estimates based on user-specified trip details. The solution is deployed as an interactive web application, enabling users to input their travel information and receive real-time price predictions.

---

## Project Details

### Problem Statement
Airline ticket prices fluctuate due to various factors such as airline, route, seasonality, and demand. Predicting these prices helps travelers make informed decisions and assists airlines in dynamic pricing strategies.

### Data Preprocessing
- **Missing Values:** Imputed using the most frequent values in each column.
- **Feature Engineering:**
  - Extracted day, month, and year from travel dates.
  - Converted categorical features (Airline, Source, Destination, etc.) to numerical values.
  - Transformed duration into total hours.
- **Dropped Columns:** Route, Dep_Time, Arrival_Time for model simplicity.

### Model Training & Evaluation
- **Models Used:**
  - Linear Regression
  - Random Forest Regressor (with GridSearchCV tuning)
  - Support Vector Regressor
  - Polynomial Regression (Degree 2 & 3)
- **Train-Test Split:** 80% training, 20% testing.
- **Evaluation Metrics:** R² score, visual inspection via plots.
- **Best Model:** Tuned Random Forest Regressor.

### Hyperparameter Tuning
GridSearchCV was used to optimize the Random Forest Regressor. Best parameters:
```
{
  'n_estimators': 200,
  'min_samples_split': 5,
  'min_samples_leaf': 1,
  'max_features': 'log2',
  'max_depth': 20
}
```

### Visualizations
- Bar plots: Airline vs Price, Number of Stops vs Price
- Correlation heatmap
- Prediction accuracy plots (scatter, line)

### Web Application
The Streamlit app provides:
- Dropdowns for airline, source, and destination
- Date picker for travel date
- Select box for ticket type (Economy/Business)
- Number inputs for adult and child count
- Slider for maximum stops
- Text input for additional info
- Predict button and output display (predicted price, comparison chart)

---

## Tech Stack
- Python 3.x
- pandas, numpy
- scikit-learn, xgboost
- matplotlib, seaborn
- Streamlit
- Jupyter Notebook

---

## Getting Started

### 1. Clone the repository
```
git clone https://github.com/DCode-v05/Flight-Price-Prediction.git
cd Flight-Price-Prediction
```

### 2. Install dependencies
```
pip install pandas numpy scikit-learn xgboost matplotlib seaborn streamlit jupyter
```

### 3. Run the Notebook or App
To train models:
```
jupyter notebook Price_Detection.ipynb
```
To launch the Streamlit app:
```
streamlit run app.py
```

---

## Usage
- Use the Jupyter notebook to explore data, train, and evaluate models.
- Use the Streamlit app to predict flight prices by entering trip details.
- Visualize model performance and feature impacts through built-in plots.

---

## Project Structure
```
Flight-Price-Prediction/
│
├── app.py                  # Streamlit web application
├── Price_Detection.ipynb   # Model training and analysis notebook
├── model/
│   └── best_model.pkl      # Trained model file
├── train/
│   ├── Data_Train.csv      # Training data (CSV)
│   └── Data_Train.xlsx     # Training data (Excel)
├── test/
│   ├── Test_set.csv        # Test data (CSV)
│   └── Test_set.xlsx       # Test data (Excel)
├── documents/
│   ├── Flight_Arch.docx    # Architecture document
│   ├── Flight_HLD.docx     # High-level design
│   ├── Flight_LLD.docx     # Low-level design
│   ├── Flight_Pro_Rep.pptx # Project report presentation
│   ├── Flight_WF.docx      # Workflow document
│   └── Flight Prediction.mp4 # Project video
├── Sample_submission.csv   # Sample output (CSV)
├── Sample_submission.xlsx  # Sample output (Excel)
└── README.md               # Project documentation
```

---

## Contributing

Contributions are welcome! To contribute:
1. Fork the repository
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to your branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request describing your changes.

---

## Contact
- **GitHub:** [DCode-v05](https://github.com/DCode-v05)
- **Email:** denistanb05@gmail.com
