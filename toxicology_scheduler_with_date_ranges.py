
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
import random
from collections import defaultdict

st.set_page_config(page_title="Toxicology On-Call Scheduler", layout="centered")
st.title("📅 Toxicology On-Call Scheduler")

first_year_fellows = st.text_input("Enter First-Year Fellows (comma-separated)", "Shin, Mahony")
second_year_fellows = st.text_input("Enter Second-Year Fellows (comma-separated)", "Burke, Johnson")
first_year_fellows = [f.strip() for f in first_year_fellows.split(",") if f.strip()]
second_year_fellows = [f.strip() for f in second_year_fellows.split(",") if f.strip()]
all_fellows = first_year_fellows + second_year_fellows

col1, col2 = st.columns(2)
with col1:
    selected_month = st.selectbox("Select Month", list(calendar.month_name)[1:], index=datetime.today().month - 1)
with col2:
    selected_year = st.number_input("Select Year", min_value=2000, max_value=2100, value=datetime.today().year)

month_number = list(calendar.month_name).index(selected_month)
start_date = datetime(selected_year, month_number, 1).date()
_, last_day = calendar.monthrange(selected_year, month_number)
end_date = datetime(selected_year, month_number, last_day).date()

clinic_date = st.date_input("Toxicology Clinic Date (usually Thursday)", datetime.today())

# === EM SHIFT INPUT SECTION ===
st.markdown("### 🚑 Emergency Medicine Shift Conflicts")
em_blocked_dict = defaultdict(set)

for fellow in all_fellows:
    with st.expander(f"Enter EM Shifts for {fellow}"):
        num_em_ranges = st.number_input(f"How many EM shifts or ranges for {fellow}?", min_value=0, max_value=30, value=0, key=f"{fellow}_em_range")
        for i in range(num_em_ranges):
            col1, col2, col3 = st.columns(3)
            with col1:
                shift_range = st.date_input(f"EM Shift #{i+1} (start–end)", key=f"{fellow}_em_range_{i}", value=(start_date, start_date))
            with col2:
                shift_start = st.time_input(f"Start time", value=datetime.strptime("07:00", "%H:%M").time(), key=f"{fellow}_em_time_{i}")
            if isinstance(shift_range, tuple):
                shift_start_date, shift_end_date = shift_range
                if shift_start < datetime.strptime("23:00", "%H:%M").time():
                    for day in pd.date_range(start=shift_start_date, end=shift_end_date).date:
                        em_blocked_dict[fellow].add(day)

# === OFF-DAY INPUT SECTION ===
st.markdown("### ❌ Off-Day Requests")
off_day_dict = defaultdict(set)

for fellow in all_fellows:
    with st.expander(f"Enter Off-Days for {fellow}"):
        num_off_ranges = st.number_input(f"How many off-day ranges for {fellow}?", min_value=0, max_value=20, value=0, key=f"{fellow}_offrange")
        for i in range(num_off_ranges):
            off_range = st.date_input(f"Off-Day Range #{i+1}", key=f"{fellow}_off_range_{i}", value=(start_date, start_date))
            if isinstance(off_range, tuple):
                off_start, off_end = off_range
                for day in pd.date_range(start=off_start, end=off_end).date:
                    off_day_dict[fellow].add(day)

# === SCHEDULING ===
if st.button("Generate Schedule"):
    if not first_year_fellows or not second_year_fellows:
        st.error("Please enter both first-year and second-year fellows.")
    else:
        all_fellows = first_year_fellows + second_year_fellows
        date_range = pd.date_range(start=start_date, end=end_date)
        days = date_range.date.tolist()
        weekend_days = [d for d in days if d.weekday() >= 5]
        weekday_days = [d for d in days if d.weekday() < 5]

        final_schedule = []
        assigned_days = set()

        def assign_shifts(dates, fellows, base_shift_dict):
            schedule = []
            date_pool = dates.copy()
            random.shuffle(date_pool)
            fellow_shift_count = defaultdict(int)
            for date in date_pool:
                random.shuffle(fellows)
                for fellow in fellows:
                    if (date not in em_blocked_dict.get(fellow, set()) and 
                        date not in off_day_dict.get(fellow, set()) and 
                        fellow_shift_count[fellow] < base_shift_dict[fellow]):
                        schedule.append({"Date": date, "Fellow": fellow})
                        fellow_shift_count[fellow] += 1
                        break
            return schedule

        total_shifts = len(weekday_days)
        n_first = len(first_year_fellows)
        n_second = len(second_year_fellows)
        total_fellows = n_first + n_second
        ideal_second = total_shifts // total_fellows
        ideal_first = ideal_second + 1
        first_targets = {f: ideal_first for f in first_year_fellows}
        second_targets = {f: ideal_second for f in second_year_fellows}
        all_targets = {**first_targets, **second_targets}

        weekday_schedule = assign_shifts(weekday_days, all_fellows, all_targets)
        assigned_days.update([entry["Date"] for entry in weekday_schedule])

        weekend_target = len(weekend_days) // len(all_fellows)
        remainder = len(weekend_days) % len(all_fellows)
        weekend_targets = {f: weekend_target for f in all_fellows}
        for f in random.sample(all_fellows, remainder):
            weekend_targets[f] += 1

        weekend_schedule = assign_shifts(weekend_days, all_fellows, weekend_targets)

        final_schedule = weekday_schedule + weekend_schedule
        df_schedule = pd.DataFrame(final_schedule).sort_values(by="Date")
        df_schedule["Day"] = pd.to_datetime(df_schedule["Date"]).dt.strftime('%A')
        df_schedule = df_schedule[["Date", "Day", "Fellow"]]

        st.success("Schedule generated successfully!")
        st.dataframe(df_schedule, use_container_width=True)

        clinic_fellow = df_schedule[df_schedule["Date"] == clinic_date]["Fellow"]
        if not clinic_fellow.empty:
            st.markdown("### 🧑‍⚕️ Clinic Day Coverage")
            st.success(f"{clinic_fellow.values[0]} is on call for the clinic day: {clinic_date.strftime('%A, %B %d, %Y')}")
        else:
            st.warning("No fellow is assigned for the clinic day you selected.")

        df_schedule["Weekend"] = pd.to_datetime(df_schedule["Date"]).dt.weekday >= 5
        summary = df_schedule.groupby("Fellow").agg(
            Total_Shifts=("Date", "count"),
            Weekend_Shifts=("Weekend", "sum")
        ).reset_index()
        st.markdown("### 📊 Shift Summary per Fellow")
        st.dataframe(summary)

        csv = df_schedule.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download Schedule as CSV",
            data=csv,
            file_name="toxicology_schedule.csv",
            mime="text/csv",
        )
