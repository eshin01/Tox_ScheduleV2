# Toxicology On-Call Scheduler (All-In-App Input)

This Streamlit application generates a monthly on-call schedule for toxicology fellows, with **no spreadsheet uploads required**.

## ✅ Features

- **Monthly scheduler** for toxicology call shifts
- Input first-year and second-year fellows directly
- Specify the **month and year** for scheduling
- Assign **one fellow per day**
- First-years get **1 more weekday shift** per month than second-years
- **Even weekend shift distribution** across all fellows
- **Enter EM shifts inline**:
  - If a shift starts **before 11PM**, that day is blocked for tox call
- **Enter off-day requests inline**:
  - Each fellow can have individual or multiple off-days
- **Clinic Day input** with automatic detection of who is on-call that day
- **Auto-labeled day of the week** for every date
- **Summary table** with total + weekend shifts per fellow
- **Downloadable schedule** as CSV

## 🚀 How to Deploy on Streamlit Cloud

1. Push the files to a GitHub repository.
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and sign in with GitHub.
3. Click “New App” and choose your repository.
4. Set the Python file as:
   ```
   toxicology_scheduler_all_inputs_inline.py
   ```
5. Click **Deploy**.

## 🗂 Files

- `toxicology_scheduler_all_inputs_inline.py`: Main application
- `requirements.txt`: Python dependencies

---

Built for scheduling toxicology fellows efficiently, with real-world academic workflows in mind.
