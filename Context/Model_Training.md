# CONTEXTO TÉCNICO FASE 3: ENTRENAMIENTO Y EVALUACIÓN DEL MODELO (SURVIVAL ANALYSIS)

## PROYECTO: MADRID LOCAL PREDICT (Premios Datos Abiertos 2026)

### 1. OBJETIVO DE ESTA FASE

Entrenar un modelo de Machine Learning capaz de predecir la **Función de Supervivencia** de un local comercial. El modelo debe aprender las relaciones no lineales entre el entorno (renta, quejas, competencia) y la longevidad del negocio.
Utilizaremos la librería especializada **`scikit-survival` (sksurv)**.

---

### 2. PREPARACIÓN DE DATOS PARA SK-SURV

La librería `sksurv` requiere un formato de datos muy específico para la variable objetivo `y`. No acepta DataFrames normales.

- **Estructura de Y:** Debe ser un array estructurado de NumPy con `dtype=[('Status', '?'), ('Survival_in_days', '<f8')]`.
  - `Status`: Booleano (True = Evento de cierre ocurrió).
  - `Survival_in_days`: Tiempo observado.
- **Split Train/Test:** Realizar una división estratificada por `evento` para asegurar que en el set de test haya suficientes casos de cierres y de supervivientes. (80% Train / 20% Test).

---

### 3. SELECCIÓN DEL ALGORITMO

Para ganar puntos en "Innovación" y capturar interacciones complejas (ej. _la renta alta es buena solo si hay poca competencia_), descartamos la Regresión de Cox lineal clásica.

- **Algoritmo Elegido:** **Random Survival Forests (RSF)** o **Gradient Boosting Survival Analysis**.
  - _Ventaja:_ Manejan automáticamente interacciones no lineales y son robustos a outliers.
  - _Implementación:_ `sksurv.ensemble.RandomSurvivalForest`.
- **Hiperparámetros Clave a tunear:**
  - `n_estimators`: Número de árboles (empezar con 100-200).
  - `min_samples_split`: Para evitar overfitting.
  - `max_depth`: Controlar la complejidad.

---

### 4. MÉTRICAS DE EVALUACIÓN (NO USAR ACCURACY)

En Survival Analysis, no podemos usar _Accuracy_ o _F1-Score_ porque tenemos datos censurados. El agente debe implementar las métricas correctas:

- **C-index (Harrell’s Concordance Index):** Mide la capacidad del modelo para ordenar correctamente los tiempos de supervivencia. (Valor 0.5 = Azar, 1.0 = Perfecto). _Objetivo: > 0.7_.
- **Integrated Brier Score (IBS):** Mide la precisión de las probabilidades predichas a lo largo del tiempo. Cuanto más bajo, mejor.

---

### 5. INTERPRETABILIDAD DEL MODELO (XAI)

Para la memoria del proyecto, necesitamos explicar **qué factores influyen más**.

- **Permutation Importance:** Calcular qué variables (Renta, Metro, Quejas...) tienen más peso en la predicción. Esto servirá para generar los "Insights" automáticos en la web.

---

### 6. EXPORTACIÓN DEL MODELO (SERIALIZACIÓN)

El modelo entrenado debe guardarse para ser consumido por la aplicación web sin necesidad de re-entrenar.

- **Formato:** `.joblib` (es más eficiente que `.pkl` para arrays de NumPy grandes dentro de los bosques aleatorios).
- **Pipeline Completo:** Guardar no solo el modelo, sino también el `OneHotEncoder` y el `StandardScaler` (si se usó) en un solo objeto `Pipeline` de scikit-learn para asegurar que los nuevos datos se transforman igual que los de entrenamiento.

### 7. OUTPUT ESPERADO DE ESTA FASE

Al finalizar, debemos tener:

1.  Un archivo `model_survival_madrid_v1.joblib` listo para producción.
2.  Un reporte (print o gráfico) con el **C-index** en el set de Test.
3.  Un gráfico de **Feature Importance** que confirme nuestras hipótesis (ej. que la cercanía al metro o la renta son importantes).
