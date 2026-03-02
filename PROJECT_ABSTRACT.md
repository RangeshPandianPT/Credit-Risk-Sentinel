# Credit Risk Sentinel

**Credit Risk Sentinel** is an end-to-end machine learning platform engineered for real-time credit risk assessment and proactive intervention. 

Leveraging advanced predictive models (**XGBoost**) with integrated explainability (**SHAP**), the system provides transparent, actionable risk scores. It features a high-performance **FastAPI** backend that ensures low-latency responses, coupled with an interactive **Streamlit** dashboard that empowers risk analysts to visualize customer profiles and trigger targeted interventions.

Orchestrated by **Airflow** for robust data pipelines and automated retraining cycles, Credit Risk Sentinel prioritizes regulatory compliance through comprehensive audit trails and simulates a production-grade **AWS cloud environment**, offering a scalable and robust solution for modern financial risk management.

### Key Features
- **Real-Time Scoring API**: Low-latency REST endpoints for instant credit risk evaluation.
- **Explainable AI**: Integrated SHAP values for transparent decision-making.
- **Interactive Dashboard**: User-friendly interface for risk analysis and manual intervention.
- **Automated Workflows**: Airflow DAGs for data ingestion, feature engineering, and model retraining.
- **Regulatory Compliance**: Built-in audit logging and data leakage checks.
- **Cloud-Ready Architecture**: Designed with simulated AWS services (SNS, S3) and Redis caching.

### Tech Stack
- **Languages**: Python
- **Frameworks**: FastAPI, Streamlit
- **ML/Data**: XGBoost, Scikit-learn, Pandas, SHAP
- **Orchestration**: Apache Airflow
- **Infrastructure**: Docker, Redis
